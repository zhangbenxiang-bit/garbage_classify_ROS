#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def image_recognition_callback(msg):
    # 收到图像识别的结果文本
    recognition_text = msg.data
    rospy.loginfo("图像识别结果：%s", recognition_text)
    
    # 把文本转发给语音合成话题
    tts_pub.publish(String(data=recognition_text))
    rospy.loginfo("已发送给语音合成，准备播报...")

if __name__ == "__main__":
    rospy.init_node("image_to_tts_bridge_node")
    
    # 订阅图像识别的结果话题（你需要改成实际的话题名）
    rospy.Subscriber("/image_recognition/result", String, image_recognition_callback)
    # 发布给语音合成的话题（和你tts_subscribe节点监听的话题一致）
    tts_pub = rospy.Publisher("/voiceWords", String, queue_size=10)
    
    rospy.loginfo("✅ 图像识别 → 语音合成 桥接节点启动成功！")
    rospy.spin()