# import subprocess

# def convert_mp3_to_wav(src, dst, sample_rate=16000):
#     """
#     Convert MP3 to WAV with specified sample rate.
    
#     Args:
#         src (str): Path to source MP3 file.
#         dst (str): Path to destination WAV file.
#         sample_rate (int): Target sample rate for the WAV file.
#     """
#     try:
#         # Construct the FFmpeg command
#         command = [
#             "ffmpeg",
#             "-i", src,          # Input file
#             "-ar", str(sample_rate),  # Set sample rate
#             "-ac", "1",         # Convert to mono
#             dst                 # Output file
#         ]
#         # Execute the command
#         subprocess.run(command, check=True)
#         print(f"Successfully converted {src} to {dst} with {sample_rate} Hz sample rate")
#     except subprocess.CalledProcessError as e:
#         print(f"FFmpeg conversion failed: {e}")
#     except FileNotFoundError:
#         print("FFmpeg is not installed or not found in PATH!")

# # Example usage
# convert_mp3_to_wav("baby_talk_fixed.mp3", "baby_talk_ds.wav", sample_rate=16000)


import anki_vector
from anki_vector import audio
import os
from dotenv import load_dotenv

# # Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../', 'configurations', '.env')

# # Load the environment variables from the .env file
load_dotenv(dotenv_path)


robot_serial = str(os.getenv("SDK_CONFIGURATION"))

with anki_vector.Robot(serial = robot_serial) as robot:
    robot.behavior.drive_off_charger()
    robot.audio.set_master_volume(audio.RobotVolumeLevel.HIGH)
    robot.behavior.say_text("Hello, I am Vector. How can I help you today?")
    robot.audio.set_master_volume(audio.RobotVolumeLevel.LOW)
    robot.behavior.say_text("Hello, I am Vector. How can I help you today?")
    
    # robot.audio.stream_wav_file('baby_talk_ds.wav')