export interface Card {
  id: number;
  classId: number;
  title: string;
  description: string;
}

export const CARDS: Card[] = [
  // === Аллигатор (classId=0) — 12 карточек ===
  { id: 1, classId: 0, title: "Миссисипский аллигатор", description: "Broad-snouted alligator lurking in murky Florida swamp, dark green scaly body with wide rounded snout" },
  { id: 2, classId: 0, title: "Китайский аллигатор", description: "Small endangered alligator in Yangtze river, dark gray armored body with bony ridges on back" },
  { id: 3, classId: 0, title: "Аллигатор в мангровых зарослях", description: "Alligator half-submerged among tangled mangrove tree roots, muddy water hiding its body" },
  { id: 4, classId: 0, title: "Аллигатор на песчаном берегу", description: "Alligator resting on warm sand at riverbank, mouth wide open showing teeth, sun reflecting on scales" },
  { id: 5, classId: 0, title: "Молодой аллигатор", description: "Juvenile alligator with bright yellow crossbands on dark green body, small and alert near water edge" },
  { id: 6, classId: 0, title: "Аллигатор в илистой воде", description: "Alligator submerged in muddy swamp with only eyes and nostrils breaking the surface like periscopes" },
  { id: 7, classId: 0, title: "Аллигатор в сумерках", description: "Alligator in twilight with eyeshine reflecting red, dark silhouette against fading evening light" },
  { id: 8, classId: 0, title: "Аллигатор с распахнутой пастью", description: "Alligator basking with enormous open jaw showing rows of sharp teeth and pink tongue" },
  { id: 9, classId: 0, title: "Аллигатор в зимней спячке", description: "Alligator in brumation half-buried in mud, only armored back plates visible above frozen surface" },
  { id: 10, classId: 0, title: "Аллигатор в зоопарке", description: "Captive alligator in concrete enclosure pond, educational sign visible, close-up of head" },
  { id: 11, classId: 0, title: "Аллигатор с детёнышами", description: "Mother alligator guarding newborn hatchlings near vegetation nest, tiny babies with yellow bands" },
  { id: 12, classId: 0, title: "Аллигатор под водой", description: "Alligator swimming just below water surface, dark elongated silhouette seen from above" },

  // === Кайман (classId=1) — 12 карточек ===
  { id: 13, classId: 1, title: "Кайман крокодиловый", description: "Spectacled caiman with bony bridge between eyes in Amazon basin, medium-sized predator in shallow water" },
  { id: 14, classId: 1, title: "Чёрный кайман", description: "Giant dark melanistic caiman from Orinoco river, near-black coloration, largest caiman species" },
  { id: 15, classId: 1, title: "Кайман Якаре", description: "Spotted caiman sunbathing on sandy Paraguay riverbank, yellow-brown pattern on dark background" },
  { id: 16, classId: 1, title: "Карликовый кайман Кювье", description: "Tiny dwarf caiman in rainforest stream, brown with black spots, less than one meter long" },
  { id: 17, classId: 1, title: "Кайман в сезон дождей", description: "Caiman swimming in flooded Amazon forest, head poking above murky brown water between trees" },
  { id: 18, classId: 1, title: "Кайман с широкой мордой", description: "Caiman with unusually wide flattened snout resting on sun-warmed rock near river" },
  { id: 19, classId: 1, title: "Молодой кайман", description: "Baby caiman with vivid yellow and black striped tail hiding among floating vegetation" },
  { id: 20, classId: 1, title: "Кайман в ночное время", description: "Caiman at night with crimson eye reflection, dark body barely visible in black water" },
  { id: 21, classId: 1, title: "Кайман на охоте", description: "Caiman stalking fish in shallow stream, belly scraping river bottom, stealthy approach" },
  { id: 22, classId: 1, title: "Кайман на бревне", description: "Caiman basking on fallen log drifting in river, tail hanging into the water" },
  { id: 23, classId: 1, title: "Кайман в мутной воде", description: "Caiman lurking in muddy water with only eyes showing, ambush predator waiting for prey" },
  { id: 24, classId: 1, title: "Кайман с открытым ртом", description: "Caiman overheating with mouth agape, thin tongue visible, cooling down on hot day" },

  // === Крокодил (classId=2) — 12 карточек ===
  { id: 25, classId: 2, title: "Нильский крокодил", description: "Large Nile crocodile with pointed V-shaped snout on African riverbank, massive tail and armored back" },
  { id: 26, classId: 2, title: "Гребнистый крокодил", description: "Saltwater crocodile in Australian estuary, enormous with prominent snout ridges, largest living reptile" },
  { id: 27, classId: 2, title: "Болотный крокодил", description: "Mugger crocodile in Indian marshland, dark olive with broad snout, basking on muddy bank" },
  { id: 28, classId: 2, title: "Кубинский крокодил", description: "Cuban crocodile with bright yellow blotches on dark body, distinctive spiky armor, highly aggressive" },
  { id: 29, classId: 2, title: "Крокодил в реке", description: "Crocodile floating in murky river with only long snout and eyes above surface, ambush mode" },
  { id: 30, classId: 2, title: "Молодой крокодил", description: "Baby crocodile with bold black and white stripes on body and tail, hiding in reeds" },
  { id: 31, classId: 2, title: "Крокодил на солнце", description: "Crocodile motionless on hot rock, mouth slightly open, scales reflecting bright sunlight" },
  { id: 32, classId: 2, title: "Крокодил с раскрытой пастью", description: "Crocodile gaping with massive jaws showing uneven teeth, powerful bite force visible" },
  { id: 33, classId: 2, title: "Крокодил под водой с рыбой", description: "Crocodile underwater holding captured fish in jaws, bubbles rising, side profile of snout" },
  { id: 34, classId: 2, title: "Острорылый крокодил", description: "Slender-snouted African crocodile with very long thin snout specialized for catching fish" },
  { id: 35, classId: 2, title: "Крокодил в сухой сезон", description: "Crocodile buried in dried cracked mud of evaporated riverbed, estivation survival mode" },
  { id: 36, classId: 2, title: "Крокодил-альбинос", description: "Rare albino crocodile in captivity with pure white skin and pink eyes, partial albinism" },
];
