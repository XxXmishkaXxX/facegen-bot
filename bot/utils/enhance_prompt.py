def enhance_prompt(user_prompt: str, style: str = "realistic") -> dict:
    base_modifiers = {
        "realistic": "portrait of a person, highly detailed, realistic skin texture, studio lighting, soft shadows, shallow depth of field, 8k",
        "artistic": "portrait, digital painting, expressive lighting, painterly, detailed brushstrokes, soft focus",
        "anime": "anime style, vibrant colors, sharp lines, expressive eyes, portrait",
        "cyberpunk": "cyberpunk style, neon lighting, futuristic background, high contrast, sharp facial features"
    }

    negative_prompt = (
        "blurry, low quality, deformed, distorted, bad anatomy, extra limbs, mutated, watermark, text, frame"
    )

    return {
        "prompt": f"{user_prompt}, {base_modifiers.get(style, base_modifiers['realistic'])}",
        "negative_prompt": negative_prompt
    }