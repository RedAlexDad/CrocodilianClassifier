import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
from django.conf import settings

_model = None
_processor = None
_text_embeddings = None
_card_texts = None
_card_ids = None
_card_titles = None

MODEL_NAME = "openai/clip-vit-base-patch32"

_RUSSIAN_TITLES = {
    1: "Миссисипский аллигатор",
    2: "Китайский аллигатор",
    3: "Аллигатор в мангровых зарослях",
    4: "Аллигатор на песчаном берегу",
    5: "Молодой аллигатор",
    6: "Аллигатор в илистой воде",
    7: "Аллигатор в сумерках",
    8: "Аллигатор с распахнутой пастью",
    9: "Аллигатор в зимней спячке",
    10: "Аллигатор в зоопарке",
    11: "Аллигатор с детёнышами",
    12: "Аллигатор под водой",
    13: "Кайман крокодиловый",
    14: "Чёрный кайман",
    15: "Кайман Якаре",
    16: "Карликовый кайман Кювье",
    17: "Кайман в сезон дождей",
    18: "Кайман с широкой мордой",
    19: "Молодой кайман",
    20: "Кайман в ночное время",
    21: "Кайман на охоте",
    22: "Кайман на бревне",
    23: "Кайман в мутной воде",
    24: "Кайман с открытым ртом",
    25: "Нильский крокодил",
    26: "Гребнистый крокодил",
    27: "Болотный крокодил",
    28: "Кубинский крокодил",
    29: "Крокодил в реке",
    30: "Молодой крокодил",
    31: "Крокодил на солнце",
    32: "Крокодил с раскрытой пастью",
    33: "Крокодил под водой с рыбой",
    34: "Острорылый крокодил",
    35: "Крокодил в сухой сезон",
    36: "Крокодил-альбинос",
}

def get_clip_model():
    global _model, _processor
    if _model is None:
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _processor = AutoProcessor.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _processor


def get_card_texts():
    global _card_texts, _card_ids, _card_titles, _text_embeddings
    if _card_texts is not None:
        return _card_texts, _card_ids, _text_embeddings

    _card_texts = [
        "Broad-snouted alligator lurking in murky Florida swamp, dark green scaly body with wide rounded snout",
        "Small endangered alligator in Yangtze river, dark gray armored body with bony ridges on back",
        "Alligator half-submerged among tangled mangrove tree roots, muddy water hiding its body",
        "Alligator resting on warm sand at riverbank, mouth wide open showing teeth, sun reflecting on scales",
        "Juvenile alligator with bright yellow crossbands on dark green body, small and alert near water edge",
        "Alligator submerged in muddy swamp with only eyes and nostrils breaking the surface like periscopes",
        "Alligator in twilight with eyeshine reflecting red, dark silhouette against fading evening light",
        "Alligator basking with enormous open jaw showing rows of sharp teeth and pink tongue",
        "Alligator in brumation half-buried in mud, only armored back plates visible above frozen surface",
        "Captive alligator in concrete enclosure pond, educational sign visible, close-up of head",
        "Mother alligator guarding newborn hatchlings near vegetation nest, tiny babies with yellow bands",
        "Alligator swimming just below water surface, dark elongated silhouette seen from above",
        "Spectacled caiman with bony bridge between eyes in Amazon basin, medium-sized predator in shallow water",
        "Giant dark melanistic caiman from Orinoco river, near-black coloration, largest caiman species",
        "Spotted caiman sunbathing on sandy Paraguay riverbank, yellow-brown pattern on dark background",
        "Tiny dwarf caiman in rainforest stream, brown with black spots, less than one meter long",
        "Caiman swimming in flooded Amazon forest, head poking above murky brown water between trees",
        "Caiman with unusually wide flattened snout resting on sun-warmed rock near river",
        "Baby caiman with vivid yellow and black striped tail hiding among floating vegetation",
        "Caiman at night with crimson eye reflection, dark body barely visible in black water",
        "Caiman stalking fish in shallow stream, belly scraping river bottom, stealthy approach",
        "Caiman basking on fallen log drifting in river, tail hanging into the water",
        "Caiman lurking in muddy water with only eyes showing, ambush predator waiting for prey",
        "Caiman overheating with mouth agape, thin tongue visible, cooling down on hot day",
        "Large Nile crocodile with pointed V-shaped snout on African riverbank, massive tail and armored back",
        "Saltwater crocodile in Australian estuary, enormous with prominent snout ridges, largest living reptile",
        "Mugger crocodile in Indian marshland, dark olive with broad snout, basking on muddy bank",
        "Cuban crocodile with bright yellow blotches on dark body, distinctive spiky armor, highly aggressive",
        "Crocodile floating in murky river with only long snout and eyes above surface, ambush mode",
        "Baby crocodile with bold black and white stripes on body and tail, hiding in reeds",
        "Crocodile motionless on hot rock, mouth slightly open, scales reflecting bright sunlight",
        "Crocodile gaping with massive jaws showing uneven teeth, powerful bite force visible",
        "Crocodile underwater holding captured fish in jaws, bubbles rising, side profile of snout",
        "Slender-snouted African crocodile with very long thin snout specialized for catching fish",
        "Crocodile buried in dried cracked mud of evaporated riverbed, estivation survival mode",
        "Rare albino crocodile in captivity with pure white skin and pink eyes, partial albinism",
    ]
    _card_ids = list(range(1, 37))
    return _card_texts, _card_ids, None


@torch.no_grad()
def encode_texts(texts: list[str]):
    model, processor = get_clip_model()
    inputs = processor(
        text=texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=77,
    )
    outputs = model.get_text_features(**inputs)
    pooled = outputs.pooler_output
    embeddings = F.normalize(pooled, dim=-1)
    return embeddings


def get_text_embeddings():
    global _text_embeddings
    if _text_embeddings is None:
        texts, _, _ = get_card_texts()
        _text_embeddings = encode_texts(texts)
    return _text_embeddings


@torch.no_grad()
def encode_image(image: Image.Image):
    model, processor = get_clip_model()
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    pooled = outputs.pooler_output
    embedding = F.normalize(pooled, dim=-1)
    return embedding


def search_similar_cards(image: Image.Image, top_k: int = 5):
    img_emb = encode_image(image)
    txt_embs = get_text_embeddings()
    texts, card_ids, _ = get_card_texts()

    similarity = (img_emb @ txt_embs.T).squeeze(0)
    scores, indices = torch.topk(similarity, k=min(top_k, len(texts)))

    results = []
    for score, idx in zip(scores.tolist(), indices.tolist()):
        card_id = card_ids[idx]
        results.append({
            "card_id": card_id,
            "title": _RUSSIAN_TITLES.get(card_id, ""),
            "description": texts[idx],
            "similarity": round(score, 4),
        })

    return results
