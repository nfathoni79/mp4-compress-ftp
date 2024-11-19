import os
import ffmpeg
import ftplib


def get_filename_list(dir_name):
    return [f for f in os.listdir(dir_name) if os.path.isfile(
        os.path.join(dir_name, f))]


def delete_all_files(dir_name):
    filename_list = get_filename_list(dir_name)
    for filename in filename_list:
        file_path = os.path.join(dir_name, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}: {e}')


def compress_video(video_full_path, output_file_name, target_size):
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    try:
        probe = ffmpeg.probe(video_full_path)

        # Video duration, in s.
        duration = float(probe['format']['duration'])

        # Audio bitrate, in bps.
        audio_bitrate = float(next(
            (s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            ['bit_rate'])

        # Target total bitrate, in bps.
        target_total_bitrate = (
            (target_size * 1024 * 8) / (1.073741824 * duration))

        # Target audio bitrate, in bps.
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate

        i = ffmpeg.input(video_full_path)
        ffmpeg.output(
            i, os.devnull, **{
                'c:v': 'libx264',
                'b:v': video_bitrate,
                'pass': 1,
                'f': 'mp4'
            }).overwrite_output().run()
        ffmpeg.output(
            i, output_file_name, **{
                'c:v': 'libx264',
                'b:v': video_bitrate,
                'pass': 2,
                'c:a': 'aac',
                'b:a': audio_bitrate
            }).overwrite_output().run()
    except FileNotFoundError as e:
        print('You do not have ffmpeg installed!', e)


def transfer_files(dir_name):
    # FTP config.
    HOSTNAME = 'ftp.dlptest.com'
    USERNAME = 'dlpuser'
    PASSWORD = 'rNrKYTX9g7z3RgJRmxWuGHbeu'

    # Connect FTP server.
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)

    # Force UTF-8 encoding.
    ftp_server.encoding = 'utf-8'

    filename_list = get_filename_list(dir_name)

    for filename in filename_list:
        # Read file in binary mode.
        with open(os.path.join(dir_name, filename), 'rb') as file:
            print(f'Transferring {filename}...')

            # Command for uploading the file "STOR filename".
            ftp_server.storbinary(f'STOR {filename}', file)

    # Get file list.
    ftp_server.dir()

    # Close FTP connection.
    ftp_server.quit()


if __name__ == '__main__':
    filename_list = get_filename_list('input')

    # Compressing all input files.
    for filename in filename_list:
        print(f'Compressing {filename}...')

        # Get file size in KB.
        filesize = os.path.getsize(os.path.join('input', filename)) / 1000

        # Compressed target file size.
        target_size = 0.1 * filesize

        # Compress video.
        compress_video(
            os.path.join('input', filename),
            os.path.join('output', filename),
            target_size)

    # Transfer all output files through FTP.
    transfer_files('output')

    # Delete all files inside input and output directories.
    delete_all_files('input')
    delete_all_files('output')
