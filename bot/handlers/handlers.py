from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from kafka.producer import producer
from utils.enhance_prompt import enhance_prompt

class Form(StatesGroup):
    ModelSelection = State()
    StyleSelection = State()
    PromptInput = State()

STYLE_MAP = {
    "🎯 Реализм": "realistic",
    "🎨 Арт": "artistic",
    "🌸 Аниме": "anime",
    "🌆 Киберпанк": "cyberpunk",
}

MODEL_MAP = {
    "Stable Diffusion 1.5": "sd15",
    "Realistic Vision 4.0": "realistic_v40",
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
        "- **Realistic Vision 4.0**: для более реалистичных изображений.\n\n"
        "Для того, чтобы начать генерацию изображений, введи команду /generate \n"
    )

@router.message(Command("generate"))
async def generate_command(message: types.Message, state: FSMContext):
    # Обработка команды /generate
    await message.answer(
        "Выберите модель для генерации изображения:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=name)] for name in MODEL_MAP.keys()
            ],
            resize_keyboard=True
        ),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(Form.ModelSelection)

@router.message(StateFilter(Form.ModelSelection))
async def choose_model(message: types.Message, state: FSMContext):
    btn_text = message.text.strip()

    if btn_text not in MODEL_MAP:
        await message.answer("Пожалуйста, выбери одну из предложенных моделей.")
        return

    internal_id = MODEL_MAP[btn_text]
    await state.update_data(selected_model_id=internal_id,
                            selected_model_human=btn_text)

    style_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=name)] for name in STYLE_MAP.keys()
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"Вы выбрали модель <b>{btn_text}</b>.\nТеперь выберите стиль изображения:",
        parse_mode=ParseMode.HTML,
        reply_markup=style_kb
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

    model_id   = data["selected_model_id"]
    model_name = data["selected_model_human"]
    style_id   = data["selected_style_id"]
    style_name = data["selected_style_human"]

    enhanced = enhance_prompt(prompt, style=style_id)

    await state.clear()

    await message.answer(
        f"Запрос принят!\n"
        f"Модель: <b>{model_name}</b>\n"
        f"Стиль: <b>{style_name}</b>\n"
        f"Промт: <i>{enhanced['prompt']}</i>",
        parse_mode=ParseMode.HTML,
    )

    await producer.send_request(
        user_id=message.chat.id,
        prompt=enhanced["prompt"],
        model=model_id,
        negative_prompt=enhanced["negative_prompt"]
    )