import cv2
import base64
import requests
import pyttsx3
import os
import time

# ===================== 配置区 =====================
QWEN_API_KEY = "sk-435bb67e9a1f45038c8391a4f2ce16b6"  # ⚠️ 请替换为你的真实 Key
MODEL_NAME = "qwen-vl-plus"
PHOTO_FILENAME = "garbage.jpg"  # 固定文件名，每次自动覆盖旧照片
# ==================================================

# 初始化语音引擎
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

# 自动切换中文语音
voices = engine.getProperty('voices')
for v in voices:
    if 'zh' in v.id.lower() or 'chinese' in v.name.lower():
        engine.setProperty('voice', v.id)
        break

def take_photo(save_path=PHOTO_FILENAME):
    """打开摄像头拍照，同名文件自动覆盖"""
    print("📸 打开摄像头，按 S 拍照，按 Q 退出")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("🗑️ 垃圾分类拍照 - S拍照 Q退出", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('s'):
            cv2.imwrite(save_path, frame)
            print(f"✅ 照片已保存: {save_path}（旧照片已覆盖）")
            break
        if k == ord('q'):
            print("⚠️ 拍照取消")
            cap.release()
            cv2.destroyAllWindows()
            return None

    cap.release()
    cv2.destroyAllWindows()
    return save_path if os.path.exists(save_path) else None

def classify_garbage(img_path):
    """调用 Qwen-VL 模型进行垃圾分类识别"""
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {QWEN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = """你是一位专业的垃圾分类助手。请分析图片中的物品，并按以下格式回答：
【物品】：简短名称
【类型】：可回收物 / 有害垃圾 / 厨余垃圾（湿垃圾） / 其他垃圾（干垃圾）
【建议】：1句话投放提醒
要求：回答简短口语化，30字以内，方便语音播报。"""
        
        data = {
            "model": MODEL_NAME,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 200
            }
        }
        
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        j = resp.json()
        
        if "choices" in j and j["choices"]:
            return j["choices"][0]["message"]["content"].strip()
        else:
            return f"❌ API错误: {j.get('message', '未知错误')}"
            
    except requests.exceptions.Timeout:
        return "⏱️ 请求超时，请检查网络"
    except Exception as e:
        return f"❌ 识别失败: {str(e)}"

def speak_text(text, retry=2):
    """语音朗读（带重试机制）"""
    print(f"🗣️ 朗读: {text}")
    for i in range(retry):
        try:
            engine.say(text)
            engine.runAndWait()
            break
        except:
            time.sleep(0.5)

def format_result(raw_text):
    """终端美化输出"""
    return raw_text.replace("【", "\n🔹 ").replace("】", ":")

def main():
    print("\n🗑️  通义千问 · 智能垃圾分类助手")
    print("=" * 50)
    
    img_path = take_photo()
    if not img_path:
        return
    
    print("🔍 正在AI识别垃圾类型...")
    result = classify_garbage(img_path)
    
    print("\n📊 识别结果：")
    print(format_result(result))
    
    speak_text("分类结果：" + result.replace("【", "").replace("】", ""))
    
    # ✅ 已移除 os.remove()，照片自动保留并覆盖
    print(f"\n📷 照片已保留在当前目录: {img_path}")
    print("✅ 完成！欢迎继续使用～")

if __name__ == "__main__":
    main()
