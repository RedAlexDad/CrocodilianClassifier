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

MODEL_NAME = "openai/clip-vit-base-patch32"

def get_clip_model():
    global _model, _processor
    if _model is None:
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _processor = AutoProcessor.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _processor


def get_card_texts():
    global _card_texts, _card_ids, _text_embeddings
    if _card_texts is not None:
        return _card_texts, _card_ids, _text_embeddings

    _card_texts = [
        "Миссисипский аллигатор, крупный аллигатор в болотах Флориды, тёмно-зелёный с широкой мордой",
        "Китайский аллигатор, небольшой аллигатор в пресных водоёмах Янцзы, тёмно-серый с костяными наростами",
        "Аллигатор в мангровых зарослях, аллигатор среди корней мангровых деревьев",
        "Аллигатор на песчаном берегу, аллигатор греющийся на солнце у кромки воды",
        "Молодой аллигатор, детёныш аллигатора с жёлтыми полосами на тёмно-зелёном теле",
        "Аллигатор в илистой воде, аллигатор выглядывающий из мутной болотной воды",
        "Аллигатор в сумерках, аллигатор в вечерних сумерках с горящими глазами",
        "Аллигатор с распахнутой пастью, аллигатор демонстрирует зубы на солнце",
        "Аллигатор в зимней спячке, аллигатор в грязи в состоянии оцепенения",
        "Аллигатор в зоопарке, аллигатор в искусственном водоёме зоопарка",
        "Аллигатор с детёнышами, взрослый аллигатор охраняет выводок у гнезда",
        "Аллигатор под водой, аллигатор под гладью воды, тёмный силуэт",
        "Очковый кайман, кайман с характерной перемычкой между глаз, болота Амазонки",
        "Чёрный кайман, крупный тёмный кайман из бассейна Ориноко",
        "Кайман Якаре, пятнистый кайман на песчаном берегу реки",
        "Карликовый кайман Кювье, маленький кайман в лесном ручье",
        "Кайман в сезон дождей, кайман в затопленном лесу, видна голова над водой",
        "Кайман с широкой мордой, кайман с приплюснутой мордой на камне у воды",
        "Молодой кайман, детёныш каймана с яркими жёлто-чёрными полосами",
        "Кайман в ночное время, кайман с горящими красными глазами в темноте",
        "Кайман на охоте, кайман подкрадывающийся к рыбе у дна",
        "Кайман на бревне, кайман греющийся на поваленном дереве у реки",
        "Кайман в мутной воде, кайман частично скрытый взбаламученной водой",
        "Кайман с открытым ртом, кайман терморегулирует с открытой пастью",
        "Нильский крокодил, крупный крокодил на берегу с V-образной мордой",
        "Гребнистый крокодил, самый большой крокодил в солёной воде Австралии",
        "Болотный крокодил, крокодил из индийских болот с широкой мордой",
        "Кубинский крокодил, редкий крокодил с яркими жёлтыми пятнами на спине",
        "Крокодил в реке, крокодил частично погружённый в мутную реку",
        "Молодой крокодил, детёныш крокодила с контрастными полосами на теле",
        "Крокодил на солнце, крокодил неподвижно лежащий на нагретом камне",
        "Крокодил с раскрытой пастью, крокодил демонстрирует мощные челюсти",
        "Крокодил с рыбой, крокодил под водой с добычей в зубах",
        "Острорылый крокодил, африканский узкорылый крокодил с длинной мордой",
        "Крокодил в сухой сезон, крокодил в пересохшем русле реки зарылся в ил",
        "Крокодил-альбинос, редкий белый крокодил с розоватыми глазами",
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
        results.append({
            "card_id": card_ids[idx],
            "title": texts[idx].split(",")[0],
            "description": texts[idx],
            "similarity": round(score, 4),
        })

    results.sort(key=lambda r: r["card_id"])
    return results
