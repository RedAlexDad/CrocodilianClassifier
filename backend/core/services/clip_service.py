import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
from django.conf import settings

_model = None
_processor = None
_text_embeddings = None
_short_text_embeddings = None
_long_text_embeddings = None

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


_CARD_TEXTS_MEDIUM = [
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

_CARD_TEXTS_SHORT = [
    "Broad-snouted alligator lurking in Florida swamp",
    "Endangered alligator in Yangtze river China",
    "Alligator half-submerged among mangrove tree roots",
    "Alligator resting on warm sand riverbank",
    "Juvenile alligator with bright yellow crossbands",
    "Alligator submerged with eyes above surface",
    "Alligator silhouette in twilight with eyeshine",
    "Alligator basking with enormous open jaw",
    "Alligator in brumation buried in frozen mud",
    "Captive alligator in concrete zoo enclosure",
    "Mother alligator guarding hatchlings near nest",
    "Alligator swimming below water surface",
    "Caiman with bony bridge between eyes",
    "Giant black melanistic caiman from Orinoco",
    "Spotted caiman sunbathing on sandy riverbank",
    "Tiny dwarf caiman in rainforest stream",
    "Caiman swimming in flooded Amazon forest",
    "Caiman with unusually wide flattened snout",
    "Baby caiman with yellow black striped tail",
    "Caiman at night with crimson eye reflection",
    "Caiman stalking fish in shallow stream",
    "Caiman basking on fallen river log",
    "Caiman lurking with only eyes showing",
    "Caiman overheating with mouth wide open",
    "Large Nile crocodile with V-shaped snout",
    "Saltwater crocodile with prominent snout ridges",
    "Mugger crocodile basking on muddy bank",
    "Cuban crocodile with yellow blotches armor",
    "Crocodile floating with long snout above surface",
    "Baby crocodile with black white stripes",
    "Crocodile motionless on hot sun rock",
    "Crocodile gaping with massive uneven teeth",
    "Crocodile underwater holding fish in jaws",
    "Slender-snouted crocodile specialized for fish",
    "Crocodile buried in dried cracked mud",
    "Albino crocodile with pure white skin",
]

_CARD_TEXTS_LONG = [
    "Large broad-snouted alligator stealthily lurking in the murky dark waters of a Florida swamp, its dark green scaly body partially submerged with only its wide rounded snout and elevated eyes visible above the surface, waiting patiently for unsuspecting prey to approach",
    "Small critically endangered Chinese alligator found in the slow-moving waters of the Yangtze river basin, featuring a dark gray heavily armored body with prominent bony ridges running along its back and a relatively short wide snout adapted for its habitat",
    "American alligator half-submerged and perfectly camouflaged among the tangled roots of mangrove trees growing along the shoreline, the dark muddy water effectively hiding the majority of its long muscular body from view above",
    "Large alligator resting motionless on the warm sun-heated sand at the edge of a riverbank, its enormous mouth wide open in a gaping display showing rows of sharp teeth while sunlight reflects brightly off its dark green scaly hide",
    "Small juvenile alligator with distinctive bright yellow crossband patterns contrasting against its dark green body, looking alert and watchful near the water's edge, still young with a relatively short snout and energetic movements",
    "Alligator fully submerged in dark muddy swamp water with only its protruding eyes and nostrils visible above the surface breaking the tension like small periscopes, perfectly adapted for ambush hunting in murky environments",
    "Alligator partially visible in the dim twilight hours with its eyes reflecting an eerie red eyeshine, a dark menacing silhouette outlined against the rapidly fading orange evening light on the horizon",
    "Large alligator basking on the bank with its enormous jaw opened wide, revealing multiple rows of sharp pointed teeth and a pink fleshy tongue inside its cavernous mouth opening",
    "Alligator in a state of brumation half-buried in thick bottom mud, only the curved armored plates of its back visible above the partially frozen surface of the winter swamp during cold months",
    "Captive alligator living in a concrete enclosure pond at a zoo facility, an educational sign visible in the background, close-up view showing the broad snout and textured scales of its head",
    "Mother alligator carefully guarding her newborn hatchlings near a vegetation nest mound built on the shore, tiny babies with bright yellow bands scattered around her protective body watching closely",
    "Alligator swimming gracefully just below the water surface, its dark elongated body forming a distinctive silhouette clearly visible from above through the clear shallow water",
    "Spectacled caiman with a prominent bony ridge bridge between its eyes typical of the species, found in the Amazon river basin, a medium-sized predator lurking in warm shallow water waiting for prey",
    "Giant dark almost black melanistic caiman from the Orinoco river system in South America, its near-black coloration making it difficult to spot in dark water, the largest species of caiman in existence",
    "Spotted caiman also known as Yacare caiman sunbathing on a sandy bank of the Paraguay river, its yellow-brown spotted pattern standing out against the dark background coloration of its body",
    "Tiny dwarf caiman of the Cuvier species found in small rainforest streams, brown colored body with black spots, measuring less than one meter in total length as a fully grown adult",
    "Caiman swimming through flooded Amazon rainforest during the rainy season, its head poking cautiously above the murky brown water surface between submerged tree trunks and vegetation",
    "Caiman with an unusually wide and flattened snout resting peacefully on a sun-warmed rock near the river's edge, its broad head distinctive compared to other caiman species in the region",
    "Baby caiman with vivid yellow and black striped tail pattern hiding cautiously among thick floating vegetation in shallow protected water near the shore away from predators",
    "Caiman seen at night with its eyes reflecting a bright crimson red color in the darkness, its dark body barely visible in the black water creating an eerie atmospheric scene",
    "Caiman actively stalking fish in a shallow clear stream, its belly scraping along the river bottom as it approaches its prey with a slow stealthy motion barely disturbing the water",
    "Caiman basking in the sun on a fallen log drifting slowly in the river, its long tail hanging down into the cool water below the log providing some temperature relief",
    "Caiman lurking in dark muddy water with only its eyes showing above the surface, an ambush predator waiting patiently for unsuspecting prey to come within striking distance",
    "Caiman overheating on a hot day with its mouth held wide open in a gaping posture, its thin pink tongue visible as it regulates body temperature through evaporative cooling behavior",
    "Large dominant Nile crocodile with a distinctly pointed V-shaped snout resting on an African riverbank, its massive powerful tail and heavily armored back clearly visible in the sunlight",
    "Enormous saltwater crocodile in an Australian estuary habitat, featuring prominent ridges above its eyes and snout, recognized as the largest living reptile species on the entire planet",
    "Mugger crocodile also known as marsh crocodile found in Indian freshwater marshlands, dark olive green coloration with a broad snout, basking on a muddy bank in the sun",
    "Cuban crocodile with bright yellow blotches scattered across its dark body, distinctive spiky armor-like scales on its back, known for being highly aggressive and agile compared to other species",
    "Crocodile floating almost completely submerged in murky river water with only its long narrow snout and eyes visible above the surface, ready in ambush mode for passing prey",
    "Baby crocodile with bold contrasting black and white striped patterns on its body and tail, hiding cautiously among dense reeds and vegetation for protection from predators",
    "Crocodile lying completely motionless on a sun-heated rock with its mouth slightly open, its hard scales reflecting the bright tropical sunlight as it thermoregulates",
    "Crocodile gaping with its massive jaws wide open revealing rows of uneven jagged teeth, demonstrating the powerful crushing bite force it possesses as a top predator",
    "Crocodile completely underwater holding a captured fish securely in its powerful jaws, bubbles rising to the surface, side profile showing its elongated snout and successful catch",
    "Slender-snouted African crocodile with a remarkably long and thin snout, an adaptation specifically evolved for catching fish in fast-moving waters with precision and speed",
    "Crocodile buried and partially hidden in dried cracked mud of an evaporated riverbed during severe drought, surviving through estivation in a reduced metabolic state waiting for rain",
    "Rare albino crocodile kept in captivity displaying pure white skin coloration and pinkish eyes, showing partial albinism with some pigment patches visible on its body",
]

_DESC_MODES = {
    "short": _CARD_TEXTS_SHORT,
    "medium": _CARD_TEXTS_MEDIUM,
    "long": _CARD_TEXTS_LONG,
}


def get_texts_for_mode(mode: str = "medium"):
    return _DESC_MODES.get(mode, _CARD_TEXTS_MEDIUM)


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


def get_text_embeddings(mode: str = "medium"):
    global _text_embeddings, _short_text_embeddings, _long_text_embeddings

    cache_map = {
        "short": "_short_text_embeddings",
        "medium": "_text_embeddings",
        "long": "_long_text_embeddings",
    }
    cache_attr = cache_map.get(mode, "_text_embeddings")
    cached = globals().get(cache_attr)
    if cached is not None:
        return cached

    texts = get_texts_for_mode(mode)
    embeddings = encode_texts(texts)
    globals()[cache_attr] = embeddings
    return embeddings


@torch.no_grad()
def encode_image(image: Image.Image):
    model, processor = get_clip_model()
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    pooled = outputs.pooler_output
    embedding = F.normalize(pooled, dim=-1)
    return embedding


def search_similar_cards(image: Image.Image, top_k: int = 5, class_id: int | None = None, desc_mode: str = "medium"):
    img_emb = encode_image(image)
    txt_embs = get_text_embeddings(desc_mode)
    texts = get_texts_for_mode(desc_mode)
    card_ids = list(range(1, 37))

    similarity = (img_emb @ txt_embs.T).squeeze(0)

    if class_id is not None:
        per_class = 12
        mask = torch.tensor([
            (cid - 1) // per_class == class_id for cid in card_ids
        ], dtype=torch.bool)
        filtered_scores = similarity[mask]
        filtered_indices = torch.where(mask)[0]
        actual_k = min(top_k, filtered_scores.size(0))
        scores, top_local = torch.topk(filtered_scores, k=actual_k)
        indices = filtered_indices[top_local]
    else:
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
