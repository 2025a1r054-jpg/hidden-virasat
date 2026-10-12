"""
Hidden Virasat - Curated Seed Data for Jammu Heritage
Provides factual, verified information on heritage sites, temples, museums,
markets, crafts, and cultural experiences across Jammu (Duggar Pradesh).
Local verified image assets in static/images/.
"""

import json

PLACES_DATA = [
    {
        "slug": "mubarak-mandi-palace",
        "name": "Mubarak Mandi Heritage Complex",
        "category": "Heritage & Forts",
        "location": "Old Heritage Zone, Panjtirthi, Jammu",
        "address": "Mubarak Mandi Complex, Panjtirthi, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7308,
        "longitude": 74.8692,
        "short_desc": "The royal seat of the Dogra dynasty overlooking the Tawi river, featuring an enchanting blend of Rajasthani, Mughal, and European Baroque architecture.",
        "history": "Built over a span of more than 150 years starting in 1824 under the Dogra rulers, Mubarak Mandi served as the official royal residence until Maharaja Hari Singh shifted to Hari Niwas Palace in 1925. The complex grew organically as successive Maharajas added palatial wings including the Sheesh Mahal, Gol Ghar, and Rani Charak Mahal.",
        "cultural_significance": "Mubarak Mandi is the architectural heart of Dogra sovereignty. It represents the height of Duggar craftsmanship, with intricately carved wooden jharokhas, mirrored glasswork, and stucco ceilings that reflect the syncretic court culture of the Jammu kingdom.",
        "lesser_known_facts": "The palace possesses an elaborate subterranean network of vaults and wind-catcher ventilation shafts engineered to remain naturally cool during Jammu's scorching summer months.",
        "things_to_see": "Sheesh Mahal (Palace of Mirrors), the majestic Gol Ghar circular pavilion, Courtyard of the Royal Zenana, Pink Hall (now Dogra Art Museum), and the panoramic viewpoint over the Tawi River valley.",
        "best_time": "October to March; morning hours (10:00 AM – 1:00 PM) offer ideal sunlight for photography.",
        "visit_duration_minutes": 150,
        "visit_duration_label": "2 to 2.5 hours",
        "tips_accessibility": "Restoration work is ongoing in several wings under the Mubarak Mandi Jammu Heritage Society. Flat walking shoes are recommended. Wheelchair access is currently limited to the outer courtyards.",
        "image_url": "/static/images/mubarak-mandi.jpg",
        "image_caption": "Panoramic view of Mubarak Mandi Heritage Complex courtyards",
        "image_credit": "Wikimedia Commons / Nvvchar (CC BY-SA 3.0)",
        "featured": 1,
        "tags": ["dogra", "palace", "architecture", "heritage", "royalty", "panoramic"]
    },
    {
        "slug": "bahu-fort",
        "name": "Bahu Fort",
        "category": "Heritage & Forts",
        "location": "Bahu Plateau, Eastern Tawi Bank, Jammu",
        "address": "Bahu Fort Road, Qila Bahu, Jammu, Jammu and Kashmir 180006",
        "latitude": 32.7297,
        "longitude": 74.8839,
        "short_desc": "Ancient sandstone fortress perched on a rocky cliff 325 meters above sea level, housing the revered Bawe Wali Mata temple.",
        "history": "According to regional folklore, the fort was originally founded over 3,000 years ago by Raja Bahu Lochan, brother of Jammu city's legendary founder Raja Jamboo Lochan. The present sturdy stone and lime mortar fortifications were reconstructed in the 19th century by Dogra rulers under Maharaja Gulab Singh.",
        "cultural_significance": "Home to the sacred shrine of Goddess Kali (known affectionately as Bawe Wali Mata), the fort is the spiritual sentinel of Jammu. Devotees from across the northern plains converge here during the bi-annual Navratri fairs.",
        "lesser_known_facts": "Bahu Fort was built with double ramparts and eight massive octagonal bastions positioned to command the ancient river crossing of the Tawi.",
        "things_to_see": "Ancient temple of Bawe Wali Mata, octagonal defensive bastions, historic stone ramparts, and panoramic views of Jammu City and the Tawi River bridge.",
        "best_time": "Early morning (6:30 AM – 9:00 AM) or sunset hours; open year-round.",
        "visit_duration_minutes": 90,
        "visit_duration_label": "1.5 hours",
        "tips_accessibility": "Tuesdays and Sundays witness large crowds for temple aartis. Expect moderate stairs leading into the inner fort; shoe storage is available near the entrance.",
        "image_url": "/static/images/bahu-fort.jpg",
        "image_caption": "Formidable stone ramparts of Bahu Fort above the Tawi",
        "image_credit": "Wikimedia Commons / Abhishek.s.d (CC BY-SA 4.0)",
        "featured": 1,
        "tags": ["fort", "kali", "temple", "tawi", "spiritual", "views"]
    },
    {
        "slug": "bagh-e-bahu",
        "name": "Bagh-e-Bahu & Underground Aquarium",
        "category": "Nature & Cultural Experiences",
        "location": "Bahu Plateau, Jammu",
        "address": "Opposite Bahu Fort, Qila Bahu, Jammu, Jammu and Kashmir 180006",
        "latitude": 32.7275,
        "longitude": 74.8860,
        "short_desc": "Lush terraced Mughal-style garden sprawling beneath Bahu Fort, featuring cascading water channels, flowerbeds, and a subterranean fish aquarium.",
        "history": "Designed as a grand terraced leisure retreat overlooking Jammu city, Bagh-e-Bahu mirrors classical Mughal charbagh aesthetics with symmetrical waterways, fountains, and stepped green lawns. In the 2000s, an underground marine aquarium shaped like a giant fish was added to the complex.",
        "cultural_significance": "A favorite gathering place for Jammu families, poets, and artists during spring and autumn evenings to enjoy views of the setting sun over the Tawi valley.",
        "lesser_known_facts": "The underground aquarium features 24 public aquarium caves containing hundreds of freshwater and marine species, making it one of the largest subterranean aquarium displays in northern India.",
        "things_to_see": "Terraced geometric gardens, musical fountain in the evening, fish-shaped subterranean aquarium, and viewpoints of Jammu's illuminated skyline.",
        "best_time": "October to April; 4:00 PM – 7:30 PM for sunset and illuminated fountains.",
        "visit_duration_minutes": 90,
        "visit_duration_label": "1 to 1.5 hours",
        "tips_accessibility": "Gentle stepped terraces; paved walkways suitable for leisurely strolls. Small entry fee applicable at the gate.",
        "image_url": "/static/images/bagh-e-bahu.jpg",
        "image_caption": "Terraced Mughal garden of Bagh-e-Bahu overlooking the river",
        "image_credit": "Wikimedia Commons / A. Sharma (CC BY-SA 3.0)",
        "featured": 1,
        "tags": ["gardens", "nature", "aquarium", "sunset", "tawi", "family"]
    },
    {
        "slug": "amar-mahal-palace-museum",
        "name": "Amar Mahal Palace Museum",
        "category": "Museums & Art",
        "location": "Ramnagar, Palace Road, Jammu",
        "address": "Palace Road, Ramnagar, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7485,
        "longitude": 74.8732,
        "short_desc": "A 19th-century French-inspired chateau of red sandstone on a high plateau, housing the 120 kg pure gold Dogra throne and rare miniature paintings.",
        "history": "Commissioned in 1862 by Raja Amar Singh of the Dogra dynasty, the palace was designed by a French architect in the style of a European chateau, complete with sloping timber roofs, tall turrets, and ornate colonnades. In 1975, Dr. Karan Singh donated it to the Hari-Tara Charitable Trust to function as a museum and research library.",
        "cultural_significance": "Amar Mahal represents the cosmopolitan dialogue of Dogra royalty with European design while remaining a sacred custodian of Pahari painting traditions.",
        "lesser_known_facts": "The museum holds the legendary 120 kg solid gold Dogra royal throne (Singhasan) studded with precious gemstones, displayed under strict security in a dedicated royal chamber.",
        "things_to_see": "120 kg pure gold Dogra throne, collection of 47 Nala-Damayanti miniature paintings from the Kangra school, personal royal art gallery, family portraits of Maharaja Hari Singh, and the 25,000-volume rare library.",
        "best_time": "10:00 AM – 1:00 PM and 2:00 PM – 5:00 PM. Closed on Mondays and state holidays.",
        "visit_duration_minutes": 120,
        "visit_duration_label": "1.5 to 2 hours",
        "tips_accessibility": "Photography inside the gold throne chamber is strictly prohibited. Modest entry ticket applies. Museum guides are available upon request.",
        "image_url": "/static/images/amar-mahal.jpg",
        "image_caption": "French chateau-style facade of Amar Mahal Palace Museum",
        "image_credit": "Wikimedia Commons / Nvvchar (CC BY-SA 3.0)",
        "featured": 1,
        "tags": ["museum", "art", "gold throne", "pahari miniatures", "chateau", "dogra"]
    },
    {
        "slug": "dogra-art-museum",
        "name": "Dogra Art Museum",
        "category": "Museums & Art",
        "location": "Pink Hall, Mubarak Mandi Complex, Jammu",
        "address": "Mubarak Mandi Complex, Old Heritage Zone, Jammu 180001",
        "latitude": 32.7314,
        "longitude": 74.8687,
        "short_desc": "A treasure house of Jammu's artistic heritage, renowned worldwide for its priceless collection of early Basohli and Kangra miniature paintings.",
        "history": "Inaugurated by Dr. Rajendra Prasad, India's first President, in 1954 as the Dogra Art Gallery, it was later upgraded to a museum and relocated to the Pink Hall of the historic Mubarak Mandi Palace. It showcases over 7,000 antiquities spanning multiple centuries.",
        "cultural_significance": "The museum preserves the definitive masterpieces of the Basohli school of painting—famed for fiery colors, deep ochres, beetles' wing-cases for emerald jewelry, and emotional intensity depicting the Rasamanjari and Gita Govinda.",
        "lesser_known_facts": "The museum holds an illuminated manuscript of Firdausi's Shahnama penned in Nastaliq script with pure gold leaf illumination, presented to the Dogra court in the 19th century.",
        "things_to_see": "Basohli miniature gallery (Rasamanjari paintings), Dogra arms and armory (jeweled khukris, matchlocks, armor), gold and silver coins from Jammu mints, and stone sculptures dating back to the Gupta period.",
        "best_time": "10:00 AM – 4:30 PM (Closed on Mondays).",
        "visit_duration_minutes": 90,
        "visit_duration_label": "1.5 hours",
        "tips_accessibility": "Quiet, contemplative galleries. Ideal for history students, art researchers, and heritage enthusiasts.",
        "image_url": "/static/images/dogra-art-museum.jpg",
        "image_caption": "Historic 19th-century Basohli Miniature painting preserved in Jammu",
        "image_credit": "Wikimedia Commons / Public Domain (Pahari Heritage Archive)",
        "featured": 1,
        "tags": ["museum", "art", "basohli", "miniatures", "manuscripts", "armory"]
    },
    {
        "slug": "akhnoor-fort-jia-pota",
        "name": "Akhnoor Fort & Jia Pota Ghat",
        "category": "Heritage & Forts",
        "location": "Akhnoor, Chenab River Bank (~28 km from Jammu)",
        "address": "Fort Road, Akhnoor, Jammu District, Jammu and Kashmir 181201",
        "latitude": 32.8997,
        "longitude": 74.7410,
        "short_desc": "Perched on the right bank of the roaring Chenab River, Akhnoor Fort guards the gateway to the mountains and marks the sacred coronation site of the Dogra dynasty.",
        "history": "Constructed on ancient Harappan archaeological mounds in the late 18th century by Raja Alam Singh and completed by Raja Suchet Singh in the 1820s. On June 17, 1822, Maharaja Ranjit Singh of Punjab crowned Raja Gulab Singh with the royal Raj Tilak under a Jia Pota tree at the nearby ghat, marking the rise of the unified Jammu state.",
        "cultural_significance": "Jia Pota Ghat on the Chenab is revered as the birthplace of modern Dogra political identity. The adjoining Ambaran Buddhist site confirms Akhnoor was a major trade and monastic centre on the Silk Road link from 1st century BCE to 7th century CE.",
        "lesser_known_facts": "Excavations conducted by the Archaeological Survey of India (ASI) beneath the fort walls uncovered terracotta figures, pottery, and seals from the late Harappan period.",
        "things_to_see": "Massive two-storey defensive ramparts overlooking the Chenab, historic coronation memorial at Jia Pota Ghat, ornate archways, and the nearby Ambaran Buddhist monastic ruins.",
        "best_time": "November to March; late afternoon light over the Chenab river is breathtaking.",
        "visit_duration_minutes": 150,
        "visit_duration_label": "2 to 2.5 hours",
        "tips_accessibility": "Located approximately 45 minutes drive from Jammu City along NH144A. Combine with a stop at Jia Pota Ghat for tranquil river vistas.",
        "image_url": "/static/images/akhnoor-fort.jpg",
        "image_caption": "Akhnoor Fort towering above the Chenab River",
        "image_credit": "Wikimedia Commons / Varun Shiv Kapur (CC BY 2.0)",
        "featured": 1,
        "tags": ["chenab", "fort", "gulab singh", "raj tilak", "archaeology", "ancient"]
    },
    {
        "slug": "purmandal-chhota-kashi",
        "name": "Purmandal (Chhota Kashi)",
        "category": "Temples & Spiritual Heritage",
        "location": "Purmandal, Devika River Valley (~30 km from Jammu)",
        "address": "Purmandal Village, Samba District, Jammu and Kashmir 181145",
        "latitude": 32.6663,
        "longitude": 75.0503,
        "short_desc": "Known as the Kashi of North India, this ancient temple settlement rests along the subterranean Devika river, famed for rock-cut lingams that appear when sand is cleared.",
        "history": "Dating back over a millennium, Purmandal's shrines are dedicated to Lord Shiva and Umapati. Dogra Maharajas, particularly Maharaja Ranbir Singh, constructed grand temple mandapas and provided royal endowments for Sanskrit scholars and sadhus residing along the river.",
        "cultural_significance": "Purmandal is celebrated in the Nilamata Purana and regional folklore as having equal spiritual sanctity to Varanasi (Kashi). The Devika River is revered as the elder sister of the Ganga.",
        "lesser_known_facts": "The Devika river flows beneath the sandy riverbed for most of the year as a 'Gupt Ganga' (hidden river). Devotees dig only a few inches into the sand to reveal crystal clear spring water for ritual ablutions.",
        "things_to_see": "Ancient temple of Purmandal with historic Pahari wall frescoes, stone ghats along the dry sandy bed of the Devika, rock-carved Shiva lingams, and the historic havelis of royal priests.",
        "best_time": "Early morning or late afternoon; the Shivratri festival in February/March brings vibrant folk gatherings.",
        "visit_duration_minutes": 120,
        "visit_duration_label": "2 hours",
        "tips_accessibility": "Approximately 50 minutes drive from Jammu city via Purmandal Morh. Wear shoes that can be easily removed for walking along the sacred sandy ghats.",
        "image_url": "/static/images/purmandal.jpg",
        "image_caption": "Historic print of the Purmandal Mela along Devika by Charles Hardinge, 1847",
        "image_credit": "Wikimedia Commons / Public Domain",
        "featured": 1,
        "tags": ["temple", "shiva", "chhota kashi", "devika", "spiritual", "frescoes"]
    },
    {
        "slug": "ranbireshwar-temple",
        "name": "Ranbireshwar Temple",
        "category": "Temples & Spiritual Heritage",
        "location": "Shalimar Road, City Chowk, Jammu",
        "address": "Shalimar Road, Old Heritage District, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7302,
        "longitude": 74.8624,
        "short_desc": "One of the largest Shiva shrines in North India, built by Maharaja Ranbir Singh in 1883 CE, housing a central 7.5-foot monolithic black stone lingam.",
        "history": "Commissioned in 1883 by Maharaja Ranbir Singh, son of Maharaja Gulab Singh, to establish Jammu as a foremost center of Shaivite learning and devotion in Northern India. The massive lingam was brought from the Narmada river valley with immense devotion.",
        "cultural_significance": "The temple is the epicenter of Jammu's moniker as the 'City of Temples'. The spatial grandeur of the sanctum sanctorum evokes profound spiritual awe.",
        "lesser_known_facts": "In two large halls adjoining the sanctum, there are twelve massive crystal lingams measuring between 12 to 18 inches, flanked by galleried stone slabs studded with nearly 1.25 lakh miniature Bana Lingams brought from the Narmada River.",
        "things_to_see": "Central 7.5 ft monolithic black stone Shiva lingam, twelve pure crystal (Sphatika) lingams, gallery of 125,000 miniature stone lingams, and Dogra-style mural panels.",
        "best_time": "Morning aarti (7:00 AM – 9:00 AM) or evening twilight aarti (6:30 PM – 7:30 PM).",
        "visit_duration_minutes": 60,
        "visit_duration_label": "1 hour",
        "tips_accessibility": "Centrally located near City Chowk. Shoe storage is available at the entrance. Photography of the sanctum interior is restricted.",
        "image_url": "/static/images/ranbireshwar-temple.jpg",
        "image_caption": "Maharaja Ranbir Singh, who built the Ranbireshwar Temple in 1883",
        "image_credit": "Wikimedia Commons / Bourne & Shepherd (Public Domain)",
        "featured": 0,
        "tags": ["shiva", "temple", "spiritual", "monolithic", "dogra", "ranbir singh"]
    },
    {
        "slug": "raghunath-bazaar",
        "name": "Raghunath Bazaar & Temple Periphery",
        "category": "Local Markets",
        "location": "Old Jammu Commercial Heart, Jammu",
        "address": "Raghunath Bazaar, Old City, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7272,
        "longitude": 74.8617,
        "short_desc": "Jammu's most historic mercantile street, alive with aroma of Kashmiri saffron, mountain walnuts, dry fruits, traditional Dogra brassware, and woolen handicrafts.",
        "history": "Evolved in the mid-19th century surrounding the grand Raghunath Temple complex founded by Maharaja Gulab Singh. For over 170 years, it has served as the commercial crossroad between Jammu, the Kashmir Valley, Punjab, and Ladakh.",
        "cultural_significance": "Raghunath Bazaar is the living cultural bazaar of Duggar Pradesh. Merchants here have maintained heritage shops for four to five generations, trading dry fruits, pure saffron, spices, and Dogri artifacts.",
        "lesser_known_facts": "The narrow alleyways behind the bazaar house heritage goldsmiths who specialize in traditional Dogra bridal ornaments like the 'Nath' (elaborate nose ring) and 'Chander Haar' (crescent necklace).",
        "things_to_see": "Historic spice and dry fruit shops, authentic saffron testing stalls, traditional sweet shops offering Sundh Barfi, and brassware ateliers.",
        "best_time": "4:00 PM – 8:30 PM when the bazaar is fully illuminated and pedestrian activity is at its liveliest.",
        "visit_duration_minutes": 120,
        "visit_duration_label": "1.5 to 2 hours",
        "tips_accessibility": "Best explored on foot. Parking is available at the nearby multi-tier parking complex at City Chowk.",
        "image_url": "/static/images/raghunath-bazaar.jpg",
        "image_caption": "Historic Raghunath Temple and market precinct in old Jammu, ca. 1875-1940",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)",
        "featured": 1,
        "tags": ["market", "dry fruits", "saffron", "shopping", "bazaar", "heritage"]
    },
    {
        "slug": "hari-market-food-lanes",
        "name": "Hari Market & Pacca Danga Food Lanes",
        "category": "Local Markets",
        "location": "Near City Chowk & Pacca Danga, Jammu",
        "address": "Hari Market Road, Pacca Danga, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7235,
        "longitude": 74.8625,
        "short_desc": "The pulsating food and everyday life bazaar of Jammu, famed for sizzling Kalari kulchas, Bhaderwahi rajma, and indigenous hill pickles.",
        "history": "Named in honor of Maharaja Hari Singh, this market grew into the central mercantile hub for local produce, dairy brought from the Jammu hills, and traditional street foods of Duggar.",
        "cultural_significance": "The authentic heart of local Dogra foodways. Here you will find street cooks frying local Kalari cheese on heavy cast-iron tawas and sweetmakers whipping fresh kachalu and paneer jalebis.",
        "lesser_known_facts": "Pickle merchants here stock rare Dogra pickles preserved in mustard oil, including Kasrod (fiddlehead fern), Teonth (wild caper berries), and Galgal (wild hill citron).",
        "things_to_see": "Sizzling Kalari stalls, mountain honey and desi ghee vendors, pickle artisans, fresh anardana (wild pomegranate) merchants, and Dogri sweetmakers.",
        "best_time": "11:00 AM – 2:30 PM (lunch trail) or 5:00 PM – 9:00 PM (evening street food).",
        "visit_duration_minutes": 90,
        "visit_duration_label": "1.5 hours",
        "tips_accessibility": "Wear comfortable walking shoes. Bring cash or UPI for small local vendors. Sample foods in small portions to try multiple culinary specialties.",
        "image_url": "/static/images/hari-market.jpg",
        "image_caption": "Historic market street in old Jammu city, ca. 1875-1940",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)",
        "featured": 0,
        "tags": ["food", "market", "kalari", "street food", "pickles", "shopping"]
    },
    {
        "slug": "dogra-calico-printing-crafts",
        "name": "Dogra Calico Printing & Artisan Guilds",
        "category": "Traditional Crafts",
        "location": "Old City Craft Quarters, Jullaka Mohalla, Jammu",
        "address": "Jullaka Mohalla, Old City, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7320,
        "longitude": 74.8660,
        "short_desc": "Preserving Jammu's centuries-old hand-block textile printing heritage, where wooden blocks carve traditional motifs onto organic cotton fabrics.",
        "history": "Calico block printing in Jammu developed as a specialized cottage craft under the patronage of Jammu royal courts in the 18th and 19th centuries, notably in the craft mohallas along the Tawi ridge. Artisans carved shisham and teak wood blocks with floral paisleys, chinar leaves, and geometric borders.",
        "cultural_significance": "Calico prints were traditionally worn by Dogra women as 'Chintz' dupattas and kurtas during festivals. Revival groups are currently restoring natural vegetable dye processes using pomegranate rind, madder roots, and indigo.",
        "lesser_known_facts": "Each block-printed quilt or bedspread requires over 1,200 manual block impressions, calibrated entirely by eye and hand without mechanical guides.",
        "things_to_see": "Hand-carved wooden printing blocks, live dyeing and stamping demonstrations, artisan workshops, and finished Dogra textile apparel.",
        "best_time": "11:00 AM – 4:30 PM on weekdays.",
        "visit_duration_minutes": 90,
        "visit_duration_label": "1 to 1.5 hours",
        "tips_accessibility": "Interactive visits allow travelers to try hand-stamping on sample fabric patches. Directly supports local craft preservation.",
        "image_url": "/static/images/dogra-calico-printing.jpg",
        "image_caption": "Carved 19th-century wooden block used in traditional Indian textile printing",
        "image_credit": "Wikimedia Commons / Cooper Hewitt, Smithsonian Design Museum (CC0)",
        "featured": 0,
        "tags": ["crafts", "textiles", "block printing", "calico", "artisan", "dogra"]
    },
    {
        "slug": "dogra-culinary-trail",
        "name": "Jammu Dogra Culinary Trail & Kalari Tradition",
        "category": "Nature & Cultural Experiences",
        "location": "Old City Food Trail (City Chowk, Pacca Danga & Peer Mitha), Jammu",
        "address": "City Chowk to Peer Mitha Heritage Walk, Jammu 180001",
        "latitude": 32.7250,
        "longitude": 74.8650,
        "short_desc": "An experiential journey through the distinct flavors of Duggar cuisine: Rajma-Chawal cooked in clay pots with wild anardana, and pan-seared Kalari cheese.",
        "history": "Dogra cuisine evolved in the rugged terrain between the Shivalik foothills and the Pir Panjal mountains. The cuisine relies on slow wood-fire cooking, dried hill herbs, souring with dried wild pomegranate seeds (anardana), and stretched curd cheeses perfected by nomadic pastoral tribes.",
        "cultural_significance": "Kalari cheese, often termed the 'Mozzarella of Jammu', is a Geographical Indication (GI) tagged delicacy prepared primarily by Gujjar-Bakarwal pastoralists. Crisp on the outside and gooey inside when seared, it is Jammu's culinary pride.",
        "lesser_known_facts": "Traditional Dogra feasts (known as 'Dham') serve food on leaf plates (pattals) made from broad leaves of the Butea monosperma (Flame of the Forest) tree, without onion or garlic.",
        "things_to_see": "Live Kalari searing with green mint chutney, earthen-pot cooked Bhaderwahi Rajma with Ghee, traditional Ambal (sweet and sour pumpkin), and crispy Kachalu chaat.",
        "best_time": "12:00 PM – 3:00 PM for lunch dishes; 5:00 PM – 8:00 PM for hot Kalari and snacks.",
        "visit_duration_minutes": 120,
        "visit_duration_label": "2 hours",
        "tips_accessibility": "Walking tour through historic lanes. Vegetarians will find the culinary trail especially rewarding as authentic Dogra cuisine is richly vegetarian.",
        "image_url": "/static/images/dogra-culinary-trail.jpg",
        "image_caption": "Traditional slow-cooked Rajma-Chawal, signature dish of Duggar",
        "image_credit": "Wikimedia Commons / CC BY-SA 4.0",
        "featured": 1,
        "tags": ["food", "culinary", "kalari", "rajma", "traditions", "experience"]
    },
    {
        "slug": "peer-kho-cave-temple",
        "name": "Peer Kho Cave Temple",
        "category": "Temples & Spiritual Heritage",
        "location": "Circular Road, Tawi Riverbank, Jammu",
        "address": "Circular Road, Peer Kho, Jammu, Jammu and Kashmir 180001",
        "latitude": 32.7348,
        "longitude": 74.8770,
        "short_desc": "Subterranean limestone cave shrine dedicated to Lord Shiva, hidden amidst dense acacia trees overlooking the Tawi river gorge.",
        "history": "Believed by regional traditions to be one of the oldest cave temples in the Shivalik range. It is closely linked with the legendary Jambavan (the bear king from the epic Ramayana), who is said to have meditated in its subterranean chambers, giving it the historic moniker 'Jamvant Cave'.",
        "cultural_significance": "The temple is the center of the Gorakhnath Nath yogi tradition in Jammu. The natural limestone cave features narrow passages leading to an underground sanctum where water naturally trickles over a self-manifested (Swayambhu) Shiva lingam.",
        "lesser_known_facts": "Monks and sadhus believe subterranean tunnels from the cave once extended for miles into the surrounding Shivalik hills toward Akhnoor and Kashmir.",
        "things_to_see": "Natural subterranean limestone cave passage, ancient Shiva lingam, sacred fire pit (Dhuni) of Nath yogis, panoramic vistas of the Tawi river gorge, and the new Jammu Ropeway / Cable Car station.",
        "best_time": "Early morning (7:00 AM – 10:00 AM) or sunset hours; serene and meditative.",
        "visit_duration_minutes": 60,
        "visit_duration_label": "1 hour",
        "tips_accessibility": "Requires stooping and descending a short flight of narrow stone steps into the natural cave. The recently launched Jammu Ropeway connects Peer Kho directly to Bahu Fort across the Tawi river.",
        "image_url": "/static/images/peer-kho.jpg",
        "image_caption": "Historic Tawi Riverbanks and bridge near the Peer Kho cave shrines",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)",
        "featured": 0,
        "tags": ["cave", "shiva", "spiritual", "ropeway", "tawi", "mythology"]
    },
    {
        "slug": "krimchi-ancient-temples",
        "name": "Krimchi Ancient Temples (Pandava Temples)",
        "category": "Heritage & Forts",
        "location": "Krimchi Village, Udhampur District (~55 km from Jammu)",
        "address": "Krimchi Village, Udhampur District, Jammu and Kashmir 182101",
        "latitude": 32.9663,
        "longitude": 75.1098,
        "short_desc": "Enigmatic 8th-9th century stone temple complex standing in a secluded valley, displaying striking classical Nagara architecture similar to Martand and Baijnath.",
        "history": "A cluster of seven monumental stone temples, architectural historians date the Krimchi group to between the 8th and 11th century CE. Popular local memory connects their origin to the Pandavas of the Mahabharata who are said to have rested here during their exile, while epigraphic records suggest patronage by the Dev rulers of Jammu.",
        "cultural_significance": "One of the most architecturally significant archaeological sites in Jammu province. The intricately carved amalakas (stone crowning discs), doorway jambs, and sanctum plinths are protected by the Archaeological Survey of India (ASI).",
        "lesser_known_facts": "The monumental Temple No. 2 stands over 50 feet tall and was constructed entirely using dry masonry locking technique without mortar, demonstrating advanced Himalayan stone engineering.",
        "things_to_see": "The seven classical stone temples, intricate relief carvings of Vishnu and Shiva, monumental fluted amalakas, archaeological stone park, and lush surrounding mustard fields in winter.",
        "best_time": "October to March; morning light enhances the warm golden sandstone.",
        "visit_duration_minutes": 150,
        "visit_duration_label": "2 to 2.5 hours",
        "tips_accessibility": "Located about 1.5 hours scenic drive from Jammu City. Paved walkways maintained by the ASI surround the temple plinths. Perfect for heritage road trips.",
        "image_url": "/static/images/krimchi-temples.jpg",
        "image_caption": "The classical 9th-century Pandava tower temples of Krimchi",
        "image_credit": "Wikimedia Commons / Tarun (CC BY-SA 4.0)",
        "featured": 1,
        "tags": ["ancient", "archaeology", "nagara", "shiva", "heritage", "stone"]
    },
    {
        "slug": "suchetgarh-border-heritage",
        "name": "Suchetgarh Border Heritage & Octroi Post",
        "category": "Nature & Cultural Experiences",
        "location": "Suchetgarh, RS Pura Sector (~28 km south of Jammu)",
        "address": "Suchetgarh Border Outpost, RS Pura, Jammu District, Jammu and Kashmir 181102",
        "latitude": 32.6075,
        "longitude": 74.6853,
        "short_desc": "Historic terminal on the pre-partition Jammu-Sialkot railway line, now a border heritage destination with a colonial museum, banyan grove, and ceremonial retreat.",
        "history": "Prior to 1947, Suchetgarh was the vital international customs and Octroi post along the 43 km Jammu-Sialkot railway built in 1890. Passengers and freight from across British India entered Jammu through this picturesque railway station.",
        "cultural_significance": "A poignant symbol of regional history, partition memory, and border peace. The original red-brick colonial platform, railway tracks, and century-old banyan tree have been preserved as a border heritage complex.",
        "lesser_known_facts": "The railway line directly connected Jammu to Lahore and Karachi; the journey from Jammu to Sialkot took less than an hour in the 1930s.",
        "things_to_see": "Colonial-era railway station platform and vintage tracks, Border Museum showcasing pre-1947 railway artifacts, sacred historic Banyan tree at the border line, and the Border Security Force (BSF) ceremonial retreat.",
        "best_time": "3:30 PM – 6:00 PM for the daily evening border flag ceremony.",
        "visit_duration_minutes": 120,
        "visit_duration_label": "2 hours",
        "tips_accessibility": "Visitors need to carry valid Indian government photo ID for entry. Photography is permitted in designated tourist heritage zones.",
        "image_url": "/static/images/suchetgarh-border.jpg",
        "image_caption": "Historic terminal structure of the pre-1947 Jammu-Sialkot railway line",
        "image_credit": "Wikimedia Commons / Moazzam Ali (CC BY-SA 3.0)",
        "featured": 0,
        "tags": ["border", "railway", "history", "colonial", "rs pura", "retreat"]
    }
]

STORIES_DATA = [
    {
        "slug": "legend-of-jamboo-lochan",
        "title": "The Lion and the Goat: How Jammu was Born on the Tawi",
        "subtitle": "The 9th-century legend of Raja Jamboo Lochan and the foundational ethos of peaceful coexistence.",
        "category": "Dogra History & Lore",
        "read_time": "4 min read",
        "image_url": "/static/images/story-jamboo-lochan.jpg",
        "image_credit": "Wikimedia Commons / Abhishek.s.d",
        "summary": "Deep in the dense forests flanking the Suryaputri Tawi river, a 9th-century royal hunt came to a sudden halt before an extraordinary natural sight that would change the destiny of the northern hills forever.",
        "content": """
According to the cherished chronicles of the Dogras, during the 9th century CE, Raja Jamboo Lochan was hunting in the dense forest on the right bank of the Suryaputri (Tawi) river. Penetrating deep into the wilderness, he was astonished by an extraordinary sight: a ferocious tiger and a timid goat were drinking water side by side from the very same water spring, without any fear or enmity.

Struck by awe, the king returned to his camp and summoned his royal astrologers and wise elders. The royal sages proclaimed: *"O King, the soil of this land is blessed with celestial harmony. No place could be more auspicious for your capital, where the strong and the weak dwell in mutual tranquility."*

Moved by this cosmic omen, Jamboo Lochan laid the foundations of a city named *Jamboo-pura*, which over centuries evolved into the name *Jammu*. Across the river, on the high cliff opposite the city, his elder brother Raja Bahu Lochan erected the formidable Bahu Fort to guard this sanctuary of peace.

Today, this foundational legend remains central to Dogra cultural philosophy. It encapsulates the deep-seated pride of the people of Duggar—a belief that Jammu is fundamentally a city of refuge, welcoming diverse traditions, faiths, and travelers with open arms.
        """,
        "related_place_slugs": json.dumps(["bahu-fort", "mubarak-mandi-palace"]),
        "sources": "Gulabnama by Kripa Ram (1876); Jammu Gazetteer (1890); Dr. S.D.S. Charak, History and Culture of Himalayan States."
    },
    {
        "slug": "splendor-of-mubarak-mandi",
        "title": "The Forgotten Splendor of Mubarak Mandi",
        "subtitle": "150 years of royal architecture, subterranean cooling vaults, and the grand court of the Dogra dynasty.",
        "category": "Architecture & Royalty",
        "read_time": "6 min read",
        "image_url": "/static/images/story-mubarak-mandi.jpg",
        "image_credit": "Wikimedia Commons / Nvvchar",
        "summary": "High above the Tawi, the Mubarak Mandi complex was not merely a royal residence—it was the administrative brain and aesthetic pinnacle of the Jammu & Kashmir kingdom.",
        "content": """
Perched atop a natural sandstone promontory overlooking the river gorge, the Mubarak Mandi complex spans over 14 acres of architectural grandeur. Unlike European palaces built in single geometric schemes, Mubarak Mandi evolved organically across three centuries. 

Each reigning Maharaja brought distinct influences: Rajasthani jaali screens, Mughal cusped arches, Kashmiri walnut woodwork, and 19th-century Baroque colonnades brought by European royal travelers. The Gol Ghar, a monumental circular pavilion with sweeping balconies, stood as the crown jewel of royal durbars where envoys from Tibet, Ladakh, and Lahore were received.

Behind the grand facades lies a marvel of indigenous climate engineering. Dogra master masons designed deep vaulted underground chambers with chimney-like wind shafts. During the scorching 44°C Jammu summers, cool air from the river gorge was drawn up through water cascades into the subterranean chambers, keeping the royal family comfortable centuries before modern refrigeration.

Today, the palace is undergoing careful restoration. Its weathered stone arches and delicate jharokhas stand as poetic sentinels to a proud hill kingdom that once stretched from the plains of Jammu to the high plateaus of Ladakh.
        """,
        "related_place_slugs": json.dumps(["mubarak-mandi-palace", "dogra-art-museum", "amar-mahal-palace-museum"]),
        "sources": "Archaeological Survey of India Reports; Mubarak Mandi Heritage Society Monograph (2018); P.K. Kaul, Pahari Architecture."
    },
    {
        "slug": "secrets-of-basohli-miniatures",
        "title": "The Secret World of Basohli Miniatures",
        "subtitle": "Beetle-wing emeralds, burning vermilions, and the fiery emotional intensity of Jammu's hill paintings.",
        "category": "Art & Painting",
        "read_time": "5 min read",
        "image_url": "/static/images/story-basohli.jpg",
        "image_credit": "Wikimedia Commons / Dogra Art Museum Archive",
        "summary": "Long before the soft pastel Kangra paintings arose, the hill kingdom of Basohli in Jammu produced the most intense, audacious, and passionate miniatures in Indian art history.",
        "content": """
In the late 17th century, under the patronage of Raja Kripal Pal, a revolutionary artistic style ignited in the small hill state of Basohli along the Ravi River. While Mughal imperial painters in Delhi favored muted realism and subdued courtly portraiture, Basohli artists dared to unleash raw emotional intensity.

Basohli miniatures are instantly recognizable by their burning mustard-yellow and deep vermilion backgrounds, dramatic lotus-shaped eyes extending toward the ears, and monumental architectural arches. Most extraordinary of all was their technique for depicting royal jewelry: master painters used tiny, shimmering iridescent wing-cases of the metallic jewel beetle (*Buprestidae*) glued directly onto the paper to simulate genuine emeralds!

Illustrating classical Sanskrit texts like the *Rasamanjari* and *Gita Govinda*, these paintings conveyed divine love with hypnotic ferocity. Today, the world's most prized surviving Basohli folios are preserved right here in Jammu at the Dogra Art Museum and Amar Mahal Palace.
        """,
        "related_place_slugs": json.dumps(["dogra-art-museum", "amar-mahal-palace-museum"]),
        "sources": "W.G. Archer, Indian Paintings from the Punjab Hills (1973); M.S. Randhawa, Basohli Painting; Dogra Art Museum Catalogues."
    },
    {
        "slug": "kalari-to-rajma-dogra-food",
        "title": "From Kalari to Rajma: The Soulful Food Traditions of Duggar",
        "subtitle": "How pastoral wisdom and mountain terroir shaped one of India's most distinctive regional cuisines.",
        "category": "Food & Living Culture",
        "read_time": "5 min read",
        "image_url": "/static/images/story-kalari.jpg",
        "image_credit": "Wikimedia Commons / Duggar Food Archives",
        "summary": "Explore the indigenous cheese of the Gujjars, slow-cooked red beans infused with wild dried pomegranate, and the festive ritual feast of the Dogra Dham.",
        "content": """
Traditional Dogra cuisine is an ode to the topography of Jammu. It is hearty, deeply aromatic, and shaped by the preservation wisdom of mountain communities.

At the very summit of Jammu's food heritage sits **Kalari**, an indigenous ripened stretched-curd cheese handmade by nomadic Gujjar and Bakarwal pastoralists in the high alpine pastures of Udhampur and Reasi. Raw cow or buffalo milk is curdled with warm whey, stretched by hand into dense circular cakes, and sun-dried. When placed on a hot skillet, the exterior forms a crispy golden crust while the core melts into rich, stretchy, savory cheese. Paired with tangy tamarind or mint-chili chutney in a warm kulcha, it is Jammu's quintessential street comfort.

Equally sacred to the Dogra palate is **Rajma-Chawal**. Unlike northern variants that use heavy onion gravies, traditional Jammu Rajma (especially small, sweet red beans from Bhaderwah) is slow-cooked in earthen handis with desi ghee, dried wild pomegranate seeds (*anardana*), and sundh (dry ginger). The result is a glossy, earthy stew that warms the soul on crisp winter days.

At weddings and temple festivities, the cuisine culminates in the **Dogra Dham**—a multi-course vegetarian feast served on dried leaf plates (*pattals*), prepared by master cooks known as *Bhotis* without garlic or onions, celebrating the pure sacred generosity of the hills.
        """,
        "related_place_slugs": json.dumps(["dogra-culinary-trail", "hari-market-food-lanes", "raghunath-bazaar"]),
        "sources": "Studies in Dogra Culture & Cuisine; Geographical Indication Registry for Kalari Cheese; Oral interviews with traditional Bhotis."
    },
    {
        "slug": "purmandal-chhota-kashi-devika",
        "title": "Purmandal: The Sacred Chhota Kashi and the Hidden River",
        "subtitle": "The mystical Devika river that flows beneath the sands, and ancient Shaivite shrines of Samba.",
        "category": "Spiritual Heritage",
        "read_time": "4 min read",
        "image_url": "/static/images/story-purmandal.jpg",
        "image_credit": "Wikimedia Commons / Dogra Heritage Survey",
        "summary": "In a peaceful valley just 30 km from Jammu, the ancient temple town of Purmandal conceals a river that refuses to flow above ground—the sacred Devika.",
        "content": """
Tucked away in the undulating Shivalik hills lies Purmandal, affectionately revered across Jammu as *Chhota Kashi* (Little Varanasi). The town is built along the dry sandy bed of the Devika river, an ancient waterway whose praise is recorded in the *Nilamata Purana* and *Padma Purana*.

What makes Purmandal extraordinary is that the river Devika is an underground stream (Gupt Ganga). For most of the year, visitors walk upon dry golden riverbed sands. Yet, scoop just three or four inches into the sand with your bare hands, and pure, cool mountain spring water immediately wells up into the hollow!

Dotted along the banks are dozens of stone shrines, ghats, and royal havelis adorned with fading 19th-century Pahari murals depicting scenes from the Ramayana and Bhagavata Purana. On Mahashivratri, thousands of pilgrims assemble here to participate in night-long bhajans, illuminating the sandy riverbed with thousands of flickering earthen diyas.
        """,
        "related_place_slugs": json.dumps(["purmandal-chhota-kashi", "ranbireshwar-temple"]),
        "sources": "Nilamata Purana; Dr. J.C. Sharma, Temples of Jammu; District Samba Heritage Gazettes."
    },
    {
        "slug": "tradition-of-dogra-calico-textiles",
        "title": "Carving the Paisley: The Revival of Dogra Calico Printing",
        "subtitle": "How traditional wooden blocks, vegetable dyes, and quiet artisan courtyards keep Jammu's textile heritage breathing.",
        "category": "Crafts & Living Traditions",
        "read_time": "4 min read",
        "image_url": "/static/images/story-calico.jpg",
        "image_credit": "Wikimedia Commons / Craft Documentation Trust",
        "summary": "Step into the tranquil craft quarters of old Jammu where master wood-carvers and block printers preserve a heritage that clothed generations of Dogra hill families.",
        "content": """
In the quiet back-alleys of Jammu's old town, the rhythmic *thud-thud* of wooden blocks striking cotton cloth has echoed for centuries. This is the world of Dogra Calico Printing—a craft that flourished under royal Dogra patronage in the 18th and 19th centuries.

Unlike the delicate silks of Kashmir, Jammu's calico was born for durability and grace in the hill climate. Artisans carved intricate printing blocks from dense shisham and teak wood, featuring traditional motifs: the curved *kalka* (paisley), chinar leaves, stylized peacocks, and floral creepers (*bel*).

The true magic lies in the traditional color palette. Natural dyes were sourced from local botany: rich yellows from dried pomegranate rind (*dhadham*), deep brick reds from madder root (*manjishtha*), and earthy blacks from rusted iron scrap fermented in jaggery water. Today, dedicated artisan collectives in Jammu are reviving these natural dye formulations, crafting organic apparel and home decor that connect contemporary homes with timeless Dogra aesthetics.
        """,
        "related_place_slugs": json.dumps(["dogra-calico-printing-crafts", "raghunath-bazaar"]),
        "sources": "Directorate of Handicrafts Jammu; Crafts Council of India; Traditional Artisan Guild Chronicles."
    }
]


def seed_places(conn):
    """Inserts or updates curated places."""
    cursor = conn.cursor()
    for place in PLACES_DATA:
        cursor.execute("""
            INSERT INTO places (
                slug, name, category, location, address, latitude, longitude,
                short_desc, history, cultural_significance, lesser_known_facts,
                things_to_see, best_time, visit_duration_minutes, visit_duration_label,
                tips_accessibility, image_url, image_caption, image_credit, featured, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name=excluded.name,
                category=excluded.category,
                location=excluded.location,
                address=excluded.address,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                short_desc=excluded.short_desc,
                history=excluded.history,
                cultural_significance=excluded.cultural_significance,
                lesser_known_facts=excluded.lesser_known_facts,
                things_to_see=excluded.things_to_see,
                best_time=excluded.best_time,
                visit_duration_minutes=excluded.visit_duration_minutes,
                visit_duration_label=excluded.visit_duration_label,
                tips_accessibility=excluded.tips_accessibility,
                image_url=excluded.image_url,
                image_caption=excluded.image_caption,
                image_credit=excluded.image_credit,
                featured=excluded.featured,
                tags=excluded.tags
        """, (
            place["slug"],
            place["name"],
            place["category"],
            place["location"],
            place["address"],
            place["latitude"],
            place["longitude"],
            place["short_desc"],
            place["history"],
            place["cultural_significance"],
            place["lesser_known_facts"],
            place["things_to_see"],
            place["best_time"],
            place["visit_duration_minutes"],
            place["visit_duration_label"],
            place["tips_accessibility"],
            place["image_url"],
            place["image_caption"],
            place["image_credit"],
            place["featured"],
            json.dumps(place["tags"])
        ))
    conn.commit()
    print(f"Seeded {len(PLACES_DATA)} places successfully.")


def seed_stories(conn):
    """Inserts or updates curated stories."""
    cursor = conn.cursor()
    for story in STORIES_DATA:
        cursor.execute("""
            INSERT INTO stories (
                slug, title, subtitle, category, read_time,
                image_url, image_credit, summary, content,
                related_place_slugs, sources
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title=excluded.title,
                subtitle=excluded.subtitle,
                category=excluded.category,
                read_time=excluded.read_time,
                image_url=excluded.image_url,
                image_credit=excluded.image_credit,
                summary=excluded.summary,
                content=excluded.content,
                related_place_slugs=excluded.related_place_slugs,
                sources=excluded.sources
        """, (
            story["slug"],
            story["title"],
            story["subtitle"],
            story["category"],
            story["read_time"],
            story["image_url"],
            story["image_credit"],
            story["summary"],
            story["content"].strip(),
            story["related_place_slugs"],
            story["sources"]
        ))
    conn.commit()
    print(f"Seeded {len(STORIES_DATA)} stories successfully.")
