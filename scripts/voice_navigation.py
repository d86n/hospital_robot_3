#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import actionlib
import speech_recognition as sr
import os
import sys
from gtts import gTTS
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

# Danh sách địa điểm và tọa độ trên bản đồ (x, y, w)
LOCATIONS = {
    "cấp cứu":      {"x": 2.33, "y": 11.9, "w": -0.00143},
    "phòng thuốc":  {"x": 8.28, "y": 13.5, "w": -0.00143},
    "x-quang":       {"x": -6.72, "y": 14.2, "w": -0.00143},
    "nhà vệ sinh":  {"x": -14.0, "y": 5.64, "w": -0.00143},
    "trạm sạc":     {"x": 10.0, "y": 0.0, "w": 1.0}   # Vị trí ban đầu
}

def speak(text):
    """Robot nói lại bằng Google Text-to-Speech (Tiếng Việt)"""
    rospy.loginfo(f"Robot nói: {text}")
    try:
        tts = gTTS(text=text, lang='vi')
        filename = "voice.mp3"
        tts.save(filename)
        os.system(f"mpg321 {filename}")
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        rospy.logerr(f"Lỗi Google TTS: {e}. Chuyển sang espeak.")
        os.system(f"espeak -v vi '{text}'")

def listen():
    """Nghe lệnh từ microphone"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        rospy.loginfo("Đang lắng nghe... (Hãy nói 'Cấp cứu', 'Phòng thuốc'...)")
        # Tự động điều chỉnh ngưỡng ồn môi trường
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            # Nghe trong vòng 5 giây
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            rospy.loginfo("Đang nhận dạng...")

            command = r.recognize_google(audio, language="vi-VN").lower()
            rospy.loginfo(f"Nghe được: {command}")
            return command
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            rospy.logwarn("Không nghe rõ câu lệnh.")
            return None
        except sr.RequestError:
            speak("Tôi bị mất kết nối internet.")
            return None

def move_to_goal(location_name, coords):
    """Gửi goal đến move_base"""
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    
    rospy.loginfo("Đang kết nối tới move_base server...")
    if not client.wait_for_server(rospy.Duration(5.0)):
        speak("Không thể kết nối tới hệ thống dẫn đường.")
        return

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    
    goal.target_pose.pose.position.x = coords['x']
    goal.target_pose.pose.position.y = coords['y']
    goal.target_pose.pose.orientation.w = coords['w']

    if (location_name == "trạm sạc"):
        speak(f"Đang di chuyển về vị trí ban đầu")
    else:
        speak(f"Đang di chuyển đến {location_name}, xin mời di chuyển cùng tôi")
    client.send_goal(goal)
    
    # Chờ robot đi đến nơi
    wait = client.wait_for_result()
    
    if not wait:
        rospy.logerr("Action server không phản hồi!")
    else:
        speak(f"Đã đến {location_name}. Xin mời vào.")
        return client.get_result()

def main():
    rospy.init_node('voice_navigation_node')
    
    rospy.sleep(1)
    speak("Xin chào. Tôi là robot bệnh viện. Bạn muốn đi đâu?")

    while not rospy.is_shutdown():
        command = listen()
        
        if command:
            found = False
            for place, coords in LOCATIONS.items():
                if place in command:
                    move_to_goal(place, coords)
                    found = True
                    break
            
            if not found:
                if "dừng lại" in command:
                    speak("Đang dừng lại.")
                elif "cảm ơn" in command:
                    speak("Xin cảm ơn. Chào tạm biệt.")
                    move_to_goal("trạm sạc", LOCATIONS["trạm sạc"])
                else:
                    speak("Xin lỗi, tôi chưa biết địa điểm đó.")
        
        rospy.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
