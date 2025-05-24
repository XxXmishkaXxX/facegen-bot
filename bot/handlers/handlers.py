import base64


from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from aiogram import F



from kafka.producer import producer
from utils.enhance_prompt import enhance_prompt

class Form(StatesGroup):
    ModelSelection = State()
    StyleSelection = State()
    PromptInput = State()
    FaceswapSource = State()
    FaceswapTarget = State() 

STYLE_MAP = {
    "🎯 Реализм": "realistic",
    "🎨 Арт": "artistic",
    "🌸 Аниме": "anime",
    "🌆 Киберпанк": "cyberpunk",
}

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Я помогу тебе создать изображения с помощью ИИ.\n\n"
        "Вот какие модели я поддерживаю:\n"
        "- **Stable Diffusion 1.5**: генерация изображений в классическом стиле.\n"
        "- **FaceFusion 3.0: замена лиц на изображении\n\n"
        "Для того, чтобы начать генерацию изображений, введи команду /generate \n"
    )

@router.message(Command("faceswap"))
async def faceswap_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Пожалуйста, отправьте фото с лицом, которое нужно заменить (источник).")
    await state.set_state(Form.FaceswapSource)

@router.message(StateFilter(Form.FaceswapSource), F.content_type == "photo")
async def faceswap_receive_source(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # берём фото с максимальным разрешением
    file_id = photo.file_id

    await state.update_data(faceswap_source_file_id=file_id)
    await message.answer("Отлично! Теперь отправьте фото, на котором нужно заменить лицо (цель).")
    await state.set_state(Form.FaceswapTarget)


@router.message(StateFilter(Form.FaceswapTarget), F.content_type == "photo")
async def faceswap_receive_target(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    target_file_id = photo.file_id

    data = await state.get_data()
    source_file_id = data.get("faceswap_source_file_id")

    if not source_file_id:
        await message.answer("Что-то пошло не так, попробуйте снова.")
        await state.clear()
        return

    await state.clear()

    bot = message.bot

    source_file = await bot.get_file(source_file_id)
    target_file = await bot.get_file(target_file_id)

    source_bytesio = await bot.download_file(source_file.file_path)
    target_bytesio = await bot.download_file(target_file.file_path)

    source_bytes = source_bytesio.read()
    target_bytes = target_bytesio.read()

    source_base64 = base64.b64encode(source_bytes).decode('utf-8')
    target_base64 = base64.b64encode(target_bytes).decode('utf-8')

    await producer.send_faceswap_request(
        user_id=message.chat.id,
        source_base64=source_base64,
        target_base64=target_base64,
    )

    await message.answer("Запрос на замену лица отправлен. Ожидайте результат.")



@router.message(Command("generate"))
async def generate_command(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text)] for text in STYLE_MAP.keys()],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Выберите стиль для генерации изображения:",
        reply_markup=keyboard,
    )
    await state.set_state(Form.StyleSelection)


@router.message(StateFilter(Form.StyleSelection))
async def choose_style(message: types.Message, state: FSMContext):
    style_text = message.text.strip()

    if style_text not in STYLE_MAP:
        await message.answer("Пожалуйста, выберите один из предложенных стилей.")
        return

    await state.update_data(selected_style_id=STYLE_MAP[style_text],
                            selected_style_human=style_text)

    await message.answer(
        "Теперь введите промт для генерации изображения.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(Form.PromptInput)


# ---------- ввод промта ---------- #
@router.message(StateFilter(Form.PromptInput))
async def get_prompt(message: types.Message, state: FSMContext):
    prompt = message.text.strip()
    data = await state.get_data()

    style_id   = data["selected_style_id"]
    style_name = data["selected_style_human"]

    enhanced = enhance_prompt(prompt, style=style_id)

    await state.clear()

    await message.answer(
        f"Запрос принят!\n"
        f"Стиль: <b>{style_name}</b>\n"
        f"Промт: <i>{enhanced['prompt']}</i>",
        parse_mode=ParseMode.HTML,
    )

    await producer.send_request(
        user_id=message.chat.id,
        prompt=enhanced["prompt"],
        negative_prompt=enhanced["negative_prompt"]
    )
