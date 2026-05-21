export interface Card {
  id: number;
  classId: number;
  title: string;
  descriptionShort: string;
  descriptionMedium: string;
  descriptionLong: string;
}

export type DescMode = 'short' | 'medium' | 'long';

export const DESC_MODES: { key: DescMode; label: string; wordRange: string }[] = [
  { key: 'short', label: 'Короткое (5-7 слов)', wordRange: '5-7' },
  { key: 'medium', label: 'Среднее (12-15 слов)', wordRange: '12-15' },
  { key: 'long', label: 'Длинное (25-35 слов)', wordRange: '25-35' },
];

export const CARDS: Card[] = [
  // === Аллигатор (classId=0) — 12 карточек ===
  {
    id: 1, classId: 0, title: "Миссисипский аллигатор",
    descriptionShort: "Broad-snouted alligator lurking in Florida swamp",
    descriptionMedium: "Broad-snouted alligator lurking in murky Florida swamp, dark green scaly body with wide rounded snout",
    descriptionLong: "Large broad-snouted alligator stealthily lurking in the murky dark waters of a Florida swamp, its dark green scaly body partially submerged with only its wide rounded snout and elevated eyes visible above the surface, waiting patiently for unsuspecting prey to approach",
  },
  {
    id: 2, classId: 0, title: "Китайский аллигатор",
    descriptionShort: "Endangered alligator in Yangtze river China",
    descriptionMedium: "Small endangered alligator in Yangtze river, dark gray armored body with bony ridges on back",
    descriptionLong: "Small critically endangered Chinese alligator found in the slow-moving waters of the Yangtze river basin, featuring a dark gray heavily armored body with prominent bony ridges running along its back and a relatively short wide snout adapted for its habitat",
  },
  {
    id: 3, classId: 0, title: "Аллигатор в мангровых зарослях",
    descriptionShort: "Alligator half-submerged among mangrove tree roots",
    descriptionMedium: "Alligator half-submerged among tangled mangrove tree roots, muddy water hiding its body",
    descriptionLong: "American alligator half-submerged and perfectly camouflaged among the tangled roots of mangrove trees growing along the shoreline, the dark muddy water effectively hiding the majority of its long muscular body from view above",
  },
  {
    id: 4, classId: 0, title: "Аллигатор на песчаном берегу",
    descriptionShort: "Alligator resting on warm sand riverbank",
    descriptionMedium: "Alligator resting on warm sand at riverbank, mouth wide open showing teeth, sun reflecting on scales",
    descriptionLong: "Large alligator resting motionless on the warm sun-heated sand at the edge of a riverbank, its enormous mouth wide open in a gaping display showing rows of sharp teeth while sunlight reflects brightly off its dark green scaly hide",
  },
  {
    id: 5, classId: 0, title: "Молодой аллигатор",
    descriptionShort: "Juvenile alligator with bright yellow crossbands",
    descriptionMedium: "Juvenile alligator with bright yellow crossbands on dark green body, small and alert near water edge",
    descriptionLong: "Small juvenile alligator with distinctive bright yellow crossband patterns contrasting against its dark green body, looking alert and watchful near the water's edge, still young with a relatively short snout and energetic movements",
  },
  {
    id: 6, classId: 0, title: "Аллигатор в илистой воде",
    descriptionShort: "Alligator submerged with eyes above surface",
    descriptionMedium: "Alligator submerged in muddy swamp with only eyes and nostrils breaking the surface like periscopes",
    descriptionLong: "Alligator fully submerged in dark muddy swamp water with only its protruding eyes and nostrils visible above the surface breaking the tension like small periscopes, perfectly adapted for ambush hunting in murky environments",
  },
  {
    id: 7, classId: 0, title: "Аллигатор в сумерках",
    descriptionShort: "Alligator silhouette in twilight with eyeshine",
    descriptionMedium: "Alligator in twilight with eyeshine reflecting red, dark silhouette against fading evening light",
    descriptionLong: "Alligator partially visible in the dim twilight hours with its eyes reflecting an eerie red eyeshine, a dark menacing silhouette outlined against the rapidly fading orange evening light on the horizon",
  },
  {
    id: 8, classId: 0, title: "Аллигатор с распахнутой пастью",
    descriptionShort: "Alligator basking with enormous open jaw",
    descriptionMedium: "Alligator basking with enormous open jaw showing rows of sharp teeth and pink tongue",
    descriptionLong: "Large alligator basking on the bank with its enormous jaw opened wide, revealing multiple rows of sharp pointed teeth and a pink fleshy tongue inside its cavernous mouth opening",
  },
  {
    id: 9, classId: 0, title: "Аллигатор в зимней спячке",
    descriptionShort: "Alligator in brumation buried in frozen mud",
    descriptionMedium: "Alligator in brumation half-buried in mud, only armored back plates visible above frozen surface",
    descriptionLong: "Alligator in a state of brumation half-buried in thick bottom mud, only the curved armored plates of its back visible above the partially frozen surface of the winter swamp during cold months",
  },
  {
    id: 10, classId: 0, title: "Аллигатор в зоопарке",
    descriptionShort: "Captive alligator in concrete zoo enclosure",
    descriptionMedium: "Captive alligator in concrete enclosure pond, educational sign visible, close-up of head",
    descriptionLong: "Captive alligator living in a concrete enclosure pond at a zoo facility, an educational sign visible in the background, close-up view showing the broad snout and textured scales of its head",
  },
  {
    id: 11, classId: 0, title: "Аллигатор с детёнышами",
    descriptionShort: "Mother alligator guarding hatchlings near nest",
    descriptionMedium: "Mother alligator guarding newborn hatchlings near vegetation nest, tiny babies with yellow bands",
    descriptionLong: "Mother alligator carefully guarding her newborn hatchlings near a vegetation nest mound built on the shore, tiny babies with bright yellow bands scattered around her protective body watching closely",
  },
  {
    id: 12, classId: 0, title: "Аллигатор под водой",
    descriptionShort: "Alligator swimming below water surface",
    descriptionMedium: "Alligator swimming just below water surface, dark elongated silhouette seen from above",
    descriptionLong: "Alligator swimming gracefully just below the water surface, its dark elongated body forming a distinctive silhouette clearly visible from above through the clear shallow water",
  },

  // === Кайман (classId=1) — 12 карточек ===
  {
    id: 13, classId: 1, title: "Кайман крокодиловый",
    descriptionShort: "Caiman with bony bridge between eyes",
    descriptionMedium: "Spectacled caiman with bony bridge between eyes in Amazon basin, medium-sized predator in shallow water",
    descriptionLong: "Spectacled caiman with a prominent bony ridge bridge between its eyes typical of the species, found in the Amazon river basin, a medium-sized predator lurking in warm shallow water waiting for prey",
  },
  {
    id: 14, classId: 1, title: "Чёрный кайман",
    descriptionShort: "Giant black melanistic caiman from Orinoco",
    descriptionMedium: "Giant dark melanistic caiman from Orinoco river, near-black coloration, largest caiman species",
    descriptionLong: "Giant dark almost black melanistic caiman from the Orinoco river system in South America, its near-black coloration making it difficult to spot in dark water, the largest species of caiman in existence",
  },
  {
    id: 15, classId: 1, title: "Кайман Якаре",
    descriptionShort: "Spotted caiman sunbathing on sandy riverbank",
    descriptionMedium: "Spotted caiman sunbathing on sandy Paraguay riverbank, yellow-brown pattern on dark background",
    descriptionLong: "Spotted caiman also known as Yacare caiman sunbathing on a sandy bank of the Paraguay river, its yellow-brown spotted pattern standing out against the dark background coloration of its body",
  },
  {
    id: 16, classId: 1, title: "Карликовый кайман Кювье",
    descriptionShort: "Tiny dwarf caiman in rainforest stream",
    descriptionMedium: "Tiny dwarf caiman in rainforest stream, brown with black spots, less than one meter long",
    descriptionLong: "Tiny dwarf caiman of the Cuvier species found in small rainforest streams, brown colored body with black spots, measuring less than one meter in total length as a fully grown adult",
  },
  {
    id: 17, classId: 1, title: "Кайман в сезон дождей",
    descriptionShort: "Caiman swimming in flooded Amazon forest",
    descriptionMedium: "Caiman swimming in flooded Amazon forest, head poking above murky brown water between trees",
    descriptionLong: "Caiman swimming through flooded Amazon rainforest during the rainy season, its head poking cautiously above the murky brown water surface between submerged tree trunks and vegetation",
  },
  {
    id: 18, classId: 1, title: "Кайман с широкой мордой",
    descriptionShort: "Caiman with unusually wide flattened snout",
    descriptionMedium: "Caiman with unusually wide flattened snout resting on sun-warmed rock near river",
    descriptionLong: "Caiman with an unusually wide and flattened snout resting peacefully on a sun-warmed rock near the river's edge, its broad head distinctive compared to other caiman species in the region",
  },
  {
    id: 19, classId: 1, title: "Молодой кайман",
    descriptionShort: "Baby caiman with yellow black striped tail",
    descriptionMedium: "Baby caiman with vivid yellow and black striped tail hiding among floating vegetation",
    descriptionLong: "Baby caiman with vivid yellow and black striped tail pattern hiding cautiously among thick floating vegetation in shallow protected water near the shore away from predators",
  },
  {
    id: 20, classId: 1, title: "Кайман в ночное время",
    descriptionShort: "Caiman at night with crimson eye reflection",
    descriptionMedium: "Caiman at night with crimson eye reflection, dark body barely visible in black water",
    descriptionLong: "Caiman seen at night with its eyes reflecting a bright crimson red color in the darkness, its dark body barely visible in the black water creating an eerie atmospheric scene",
  },
  {
    id: 21, classId: 1, title: "Кайман на охоте",
    descriptionShort: "Caiman stalking fish in shallow stream",
    descriptionMedium: "Caiman stalking fish in shallow stream, belly scraping river bottom, stealthy approach",
    descriptionLong: "Caiman actively stalking fish in a shallow clear stream, its belly scraping along the river bottom as it approaches its prey with a slow stealthy motion barely disturbing the water",
  },
  {
    id: 22, classId: 1, title: "Кайман на бревне",
    descriptionShort: "Caiman basking on fallen river log",
    descriptionMedium: "Caiman basking on fallen log drifting in river, tail hanging into the water",
    descriptionLong: "Caiman basking in the sun on a fallen log drifting slowly in the river, its long tail hanging down into the cool water below the log providing some temperature relief",
  },
  {
    id: 23, classId: 1, title: "Кайман в мутной воде",
    descriptionShort: "Caiman lurking with only eyes showing",
    descriptionMedium: "Caiman lurking in muddy water with only eyes showing, ambush predator waiting for prey",
    descriptionLong: "Caiman lurking in dark muddy water with only its eyes showing above the surface, an ambush predator waiting patiently for unsuspecting prey to come within striking distance",
  },
  {
    id: 24, classId: 1, title: "Кайман с открытым ртом",
    descriptionShort: "Caiman overheating with mouth wide open",
    descriptionMedium: "Caiman overheating with mouth agape, thin tongue visible, cooling down on hot day",
    descriptionLong: "Caiman overheating on a hot day with its mouth held wide open in a gaping posture, its thin pink tongue visible as it regulates body temperature through evaporative cooling behavior",
  },

  // === Крокодил (classId=2) — 12 карточек ===
  {
    id: 25, classId: 2, title: "Нильский крокодил",
    descriptionShort: "Large Nile crocodile with V-shaped snout",
    descriptionMedium: "Large Nile crocodile with pointed V-shaped snout on African riverbank, massive tail and armored back",
    descriptionLong: "Large dominant Nile crocodile with a distinctly pointed V-shaped snout resting on an African riverbank, its massive powerful tail and heavily armored back clearly visible in the sunlight",
  },
  {
    id: 26, classId: 2, title: "Гребнистый крокодил",
    descriptionShort: "Saltwater crocodile with prominent snout ridges",
    descriptionMedium: "Saltwater crocodile in Australian estuary, enormous with prominent snout ridges, largest living reptile",
    descriptionLong: "Enormous saltwater crocodile in an Australian estuary habitat, featuring prominent ridges above its eyes and snout, recognized as the largest living reptile species on the entire planet",
  },
  {
    id: 27, classId: 2, title: "Болотный крокодил",
    descriptionShort: "Mugger crocodile basking on muddy bank",
    descriptionMedium: "Mugger crocodile in Indian marshland, dark olive with broad snout, basking on muddy bank",
    descriptionLong: "Mugger crocodile also known as marsh crocodile found in Indian freshwater marshlands, dark olive green coloration with a broad snout, basking on a muddy bank in the sun",
  },
  {
    id: 28, classId: 2, title: "Кубинский крокодил",
    descriptionShort: "Cuban crocodile with yellow blotches armor",
    descriptionMedium: "Cuban crocodile with bright yellow blotches on dark body, distinctive spiky armor, highly aggressive",
    descriptionLong: "Cuban crocodile with bright yellow blotches scattered across its dark body, distinctive spiky armor-like scales on its back, known for being highly aggressive and agile compared to other species",
  },
  {
    id: 29, classId: 2, title: "Крокодил в реке",
    descriptionShort: "Crocodile floating with long snout above surface",
    descriptionMedium: "Crocodile floating in murky river with only long snout and eyes above surface, ambush mode",
    descriptionLong: "Crocodile floating almost completely submerged in murky river water with only its long narrow snout and eyes visible above the surface, ready in ambush mode for passing prey",
  },
  {
    id: 30, classId: 2, title: "Молодой крокодил",
    descriptionShort: "Baby crocodile with black white stripes",
    descriptionMedium: "Baby crocodile with bold black and white stripes on body and tail, hiding in reeds",
    descriptionLong: "Baby crocodile with bold contrasting black and white striped patterns on its body and tail, hiding cautiously among dense reeds and vegetation for protection from predators",
  },
  {
    id: 31, classId: 2, title: "Крокодил на солнце",
    descriptionShort: "Crocodile motionless on hot sun rock",
    descriptionMedium: "Crocodile motionless on hot rock, mouth slightly open, scales reflecting bright sunlight",
    descriptionLong: "Crocodile lying completely motionless on a sun-heated rock with its mouth slightly open, its hard scales reflecting the bright tropical sunlight as it thermoregulates",
  },
  {
    id: 32, classId: 2, title: "Крокодил с раскрытой пастью",
    descriptionShort: "Crocodile gaping with massive uneven teeth",
    descriptionMedium: "Crocodile gaping with massive jaws showing uneven teeth, powerful bite force visible",
    descriptionLong: "Crocodile gaping with its massive jaws wide open revealing rows of uneven jagged teeth, demonstrating the powerful crushing bite force it possesses as a top predator",
  },
  {
    id: 33, classId: 2, title: "Крокодил под водой с рыбой",
    descriptionShort: "Crocodile underwater holding fish in jaws",
    descriptionMedium: "Crocodile underwater holding captured fish in jaws, bubbles rising, side profile of snout",
    descriptionLong: "Crocodile completely underwater holding a captured fish securely in its powerful jaws, bubbles rising to the surface, side profile showing its elongated snout and successful catch",
  },
  {
    id: 34, classId: 2, title: "Острорылый крокодил",
    descriptionShort: "Slender-snouted crocodile specialized for fish",
    descriptionMedium: "Slender-snouted African crocodile with very long thin snout specialized for catching fish",
    descriptionLong: "Slender-snouted African crocodile with a remarkably long and thin snout, an adaptation specifically evolved for catching fish in fast-moving waters with precision and speed",
  },
  {
    id: 35, classId: 2, title: "Крокодил в сухой сезон",
    descriptionShort: "Crocodile buried in dried cracked mud",
    descriptionMedium: "Crocodile buried in dried cracked mud of evaporated riverbed, estivation survival mode",
    descriptionLong: "Crocodile buried and partially hidden in dried cracked mud of an evaporated riverbed during severe drought, surviving through estivation in a reduced metabolic state waiting for rain",
  },
  {
    id: 36, classId: 2, title: "Крокодил-альбинос",
    descriptionShort: "Albino crocodile with pure white skin",
    descriptionMedium: "Rare albino crocodile in captivity with pure white skin and pink eyes, partial albinism",
    descriptionLong: "Rare albino crocodile kept in captivity displaying pure white skin coloration and pinkish eyes, showing partial albinism with some pigment patches visible on its body",
  },
];
