from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

# 创建 KeyBindings 实例来处理按键
kb = KeyBindings()

# 使用 Shift+Tab (BackTab) 进行换行
@kb.add(Keys.BackTab)
def _(event):
    event.current_buffer.insert_text('\n')

# 创建 PromptSession 实例
session = PromptSession(key_bindings=kb)

# 获取多行输入
text = session.prompt("请输入文本 (Shift+Tab 换行, Enter 提交): ")

print("\n您输入了：")
print(text)
