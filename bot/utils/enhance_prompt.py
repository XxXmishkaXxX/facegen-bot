def enhance_prompt(user_prompt: str, style: str = "realistic") -> dict:
    base_modifiers = {
        "realistic": "portrait, upper body, from head to waist, face centered, ultra realistic, high detail, 8k resolution, photorealistic, natural skin texture, perfect facial proportions, realistic lighting and shadows, sharp facial features, soft background blur, depth of field, subtle expression, cinematic lighting, Nikon D850, masterpiece, best quality",
        "artistic": "portrait, head and torso view, upper body only, focus on face, expressive facial expression, concept art style, intricate details, digital painting, smooth brushwork, fantasy color palette, artstation trending, elegant lighting, beautiful composition, high detail, masterpiece",
        "anime": "anime portrait, bust shot, head and torso view, focus on face, large expressive eyes, soft facial features, vibrant cel-shaded colors, detailed anime background, pixiv trending style, studio ghibli lighting, perfect composition, upper body only, clean lines, high detail, beautiful anime girl/boy",
        "cyberpunk": "cyberpunk portrait, bust shot, from head to waist, neon-lit background, glowing tattoos or implants, sharp facial expression, futuristic city vibes, synthwave lighting (pink, blue, violet), cybernetic details, soft neon reflections on skin, dystopian style, ultra detailed face, dark aesthetic, cinematic, blade runner style"
    }

    negative_prompt = (
        "blurry, low quality, deformed, distorted, bad anatomy, extra limbs, mutated, watermark, text, frame"
    )

    return {
        "prompt": f"{user_prompt}, {base_modifiers.get(style, base_modifiers['realistic'])}",
        "negative_prompt": negative_prompt
    }
