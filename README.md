## Cài đặt
```
sudo apt-get update
sudo apt-get install ros-noetic-navigation
sudo apt-get install ros-noetic-gmapping
sudo apt-get install ros-noetic-openslam-gmapping
sudo apt-get install ros-noetic-teleop-twist-keyboard
sudo apt-get install -y espeak portaudio19-dev python3-pyaudio
pip3 install SpeechRecognition
pip3 install gTTS
sudo apt-get install mpg321
```

## Cấp quyền thực thi cho file script
```
roscd hospital_robot
chmod +x scripts/voice_navigation.py
```