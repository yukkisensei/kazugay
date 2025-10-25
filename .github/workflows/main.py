import os

import asyncio

import importlib

from dotenv import load_dotenv

import discord

from discord.ext import commands



load_dotenv()



DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN")

print("DEBUG TOKEN START:", repr(DISCORD_TOKEN)[:40])



if not DISCORD_TOKEN:

    raise SystemExit("❌ Không tìm thấy DISCORD_TOKEN trong .env. Thêm DISCORD_TOKEN=your_token_here")





# --- Cài đặt Intents ---

intents = discord.Intents.default()

intents.message_content = True

intents.guilds = True

intents.members = True



bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)



@bot.event

async def on_ready():

    print(f"✅ Bot ready: {bot.user} (ID: {bot.user.id})")

    print("-" * 20)



async def safe_setup_module(name: str):

    """

    Thử load module `name` theo nhiều cách:

    - Nếu module.setup(bot) có sẵn -> gọi (hỗ trợ cả coroutine)

    - Nếu module có class AI hoặc Lenh -> tạo instance và add_cog

    - Nếu module có hàm setup_commands -> gọi (tương thích với code cũ)

    """

    try:

        module_name = name.replace(os.path.sep, '.')

        mod = importlib.import_module(module_name)

        print(f"🔄 Đang tải module: {module_name}")

    except Exception as e:

        print(f" LỖI: Không thể import module {name}: {e}")

        return



    # Nếu có setup(bot)

    if hasattr(mod, "setup"):

        try:

            maybe = mod.setup(bot)

            if asyncio.iscoroutine(maybe):

                await maybe

            print(f"  -> Đã gọi setup() thành công cho {module_name}")

            return

        except Exception as e:

            print(f"  LỖI: khi gọi setup() cho {module_name}: {e}")



    # Nếu có setup_commands (những code cũ)

    if hasattr(mod, "setup_commands"):

        try:

            maybe = mod.setup_commands(bot)

            if asyncio.iscoroutine(maybe):

                await maybe

            print(f"  -> Đã gọi setup_commands() (cũ) thành công cho {module_name}")

            return

        except Exception as e:

            print(f"  LỖI khi gọi {module_name}.setup_commands: {e}")



    # Thử tìm class AI / Lenh để add_cog

    for class_name in ("AI", "Lenh", "Commands", "Cog"):

        cls = getattr(mod, class_name, None)

        if cls and isinstance(cls, type):

            try:

                await bot.add_cog(cls(bot))

                print(f"  -> Đã thêm cog {class_name} từ {module_name}")

                return

            except Exception as e:

                print(f"  LỖI: Không thể add_cog {class_name} từ {module_name}: {e}")



    print(f"  CẢNH BÁO: Module {module_name} được load nhưng không tìm thấy hàm setup / class cog phù hợp.")



async def main():

    print("--- Bắt đầu khởi động bot ---")

    

    # Giữ lại cách làm cũ nếu bạn thích sự đơn giản

    module_files = ["ai.py", "lenh.py"]



    for m_file in module_files:

        if os.path.exists(m_file):

            await safe_setup_module(m_file.replace(".py", ""))

        else:

            print(f"CẢNH BÁO: Không tìm thấy file module '{m_file}', bỏ qua.")

    

    print("-" * 20)

    # Khởi động bot

    await bot.start(DISCORD_TOKEN)



if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n--- Bot đã dừng bởi người dùng ---")



