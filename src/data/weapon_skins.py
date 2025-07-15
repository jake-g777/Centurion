"""
CS2 Weapon Skins Database
Contains popular weapon skins organized by weapon categories
"""

WEAPON_SKINS = {
    "AK-47": [
        "Redline",
        "Fire Serpent",
        "Bloodsport",
        "Asiimov",
        "Vulcan",
        "Neon Revolution",
        "The Empress",
        "Slate",
        "Gold Arabesque",
        "Case Hardened",
        "Fade",
        "Dragon Tattoo",
        "Jaguar",
        "Aquamarine Revenge",
        "Neon Rider",
        "Wasteland Rebel",
        "Elite Build",
        "Point Disarray",
        "Fuel Injector",
        "Hydroponic"
    ],
    "AWP": [
        "Dragon Lore",
        "Medusa",
        "Fade",
        "Asiimov",
        "Hyper Beast",
        "Lightning Strike",
        "Gungnir",
        "Wildfire",
        "Neo-Noir",
        "Oni Taiji",
        "Graphite",
        "BOOM",
        "Pink DDPAT",
        "Redline",
        "Man-o'-war",
        "Elite Build",
        "Sun in Leo",
        "Corticera",
        "Snake Camo",
        "Electric Hive"
    ],
    "M4A4": [
        "Howl",
        "Asiimov",
        "Desolate Space",
        "Poseidon",
        "The Emperor",
        "Evil Daimyo",
        "Daybreak",
        "Neo-Noir",
        "Buzz Kill",
        "Desert Storm",
        "Zirka",
        "X-Ray",
        "Modern Hunter",
        "Faded Zebra",
        "Tornado",
        "Griffin",
        "Bullet Rain",
        "Dragon King",
        "Spider Lily",
        "In Living Color"
    ],
    "M4A1-S": [
        "Hot Rod",
        "Hyper Beast",
        "Cyrex",
        "Master Piece",
        "Knight",
        "Golden Coil",
        "Icarus Fell",
        "Chantico's Fire",
        "Mecha Industries",
        "Decimator",
        "Atomic Alloy",
        "Guardian",
        "Basilisk",
        "Bright Water",
        "Blood Tiger",
        "Dark Water",
        "Boreal Forest",
        "Varicamo",
        "Nitro",
        "Flashback"
    ],
    "Desert Eagle": [
        "Blaze",
        "Golden Koi",
        "Crimson Web",
        "Fade",
        "Code Red",
        "Hypnotic",
        "Sunset Storm",
        "Ocean Drive",
        "Kumicho Dragon",
        "Midnight Storm",
        "Heirloom",
        "Meteorite",
        "Naga",
        "Urban Rubble",
        "Mudder",
        "Cobalt Disruption",
        "Bronze Deco",
        "Pilot",
        "Scorched",
        "Urban DDPAT"
    ],
    "USP-S": [
        "Kill Confirmed",
        "Neo-Noir",
        "Caiman",
        "Overgrowth",
        "Cyrex",
        "Guardian",
        "Orion",
        "Road Rash",
        "Serum",
        "Stainless",
        "Dark Water",
        "Blood Tiger",
        "Para Green",
        "Forest Leaves",
        "Tornado",
        "Blueprint",
        "Check Engine",
        "Monster Callup",
        "Business Class",
        "Royal Blue"
    ],
    "Glock-18": [
        "Fade",
        "Dragon Tattoo",
        "Twilight Galaxy",
        "Water Elemental",
        "Reactor",
        "Wraiths",
        "Brass",
        "Sand Dune",
        "Groundwater",
        "Steel Disruption",
        "Blue Fissure",
        "Bunsen Burner",
        "Ironwork",
        "Weasel",
        "Candy Apple",
        "Death Rattle",
        "Vogue",
        "Snack Attack",
        "High Beam",
        "Off World"
    ],
    "P250": [
        "Asiimov",
        "Undertow",
        "Whiteout",
        "Nuclear Threat",
        "Splash",
        "Mehndi",
        "Valence",
        "Muertos",
        "Wingshot",
        "Crimson Kimono",
        "Hive",
        "Steel Disruption",
        "Boreal Forest",
        "Sand Dune",
        "Gunsmoke",
        "Supernova",
        "Red Rock",
        "Facets",
        "Mint Kimono",
        "Visions"
    ],
    "AUG": [
        "Akihabara Accept",
        "Hot Rod",
        "Chameleon",
        "Bengal Tiger",
        "Carved Jade",
        "Anodized Navy",
        "Wings",
        "Storm",
        "Torque",
        "Radiation Hazard",
        "Daedalus",
        "Condemned",
        "Ricochet",
        "Syd Mead",
        "Triqua",
        "Colony IV",
        "Sweeper",
        "Copperhead",
        "Stattrak",
        "Random Access"
    ],
    "SG 553": [
        "Tiger Moth",
        "Cyrex",
        "Pulse",
        "Tornado",
        "Ultraviolet",
        "Anodized Navy",
        "Damascus Steel",
        "Fallout Warning",
        "Gator Mesh",
        "Waves Perforated",
        "Integrale",
        "Triscope",
        "Phantom",
        "Army Sheen",
        "Bulldozer",
        "Traveler",
        "Hypnotic",
        "Barricade",
        "Aerial",
        "Heavy Metal"
    ],
    "FAMAS": [
        "Pulse",
        "Styx",
        "Sergeant",
        "Neural Net",
        "Roll Cage",
        "Mekanism",
        "Teardown",
        "Survivor Z",
        "Doomkitty",
        "Hexane",
        "Spitfire",
        "Afterimage",
        "Valence",
        "Contrast Spray",
        "Djinn",
        "Macabre",
        "Commemoration",
        "Prime Conspiracy",
        "Eye of Athena",
        "Rally"
    ]
}

# Popular weapon categories for quick selection
WEAPON_CATEGORIES = {
    "Rifles": ["AK-47", "AWP", "M4A4", "M4A1-S", "AUG", "SG 553", "FAMAS", "GALIL AR", "SCAR-20", "G3SG1"],
    "Pistols": ["Desert Eagle", "USP-S", "Glock-18", "P250", "Tec-9", "Five-SeveN", "CZ75-Auto", "R8 Revolver", "Dual Berettas"],
    "SMGs": ["MP9", "MAC-10", "MP7", "UMP-45", "P90", "PP-Bizon"],
    "Heavy": ["Nova", "XM1014", "Sawed-Off", "MAG-7", "M249", "Negev"],
    "Knives": ["Karambit", "M9 Bayonet", "Butterfly Knife", "Bayonet", "Flip Knife", "Gut Knife", "Shadow Daggers", "Bowie Knife", "Falchion Knife", "Huntsman Knife"]
}

# Popular skin collections
SKIN_COLLECTIONS = {
    "Operation Collections": ["Operation Bravo", "Operation Phoenix", "Operation Breakout", "Operation Vanguard", "Operation Bloodhound"],
    "Community Collections": ["Community Collection 1", "Community Collection 2", "Community Collection 3"],
    "Case Collections": ["CS:GO Weapon Case", "CS:GO Weapon Case 2", "CS:GO Weapon Case 3", "eSports 2013 Case", "eSports 2013 Winter Case"],
    "Special Collections": ["The Bravo Collection", "The Phoenix Collection", "The Breakout Collection", "The Vanguard Collection"]
}

def get_all_weapons():
    """Get all available weapons"""
    return list(WEAPON_SKINS.keys())

def get_weapon_skins(weapon: str):
    """Get all skins for a specific weapon"""
    return WEAPON_SKINS.get(weapon, [])

def get_weapons_by_category(category: str):
    """Get weapons by category"""
    return WEAPON_CATEGORIES.get(category, [])

def get_all_categories():
    """Get all weapon categories"""
    return list(WEAPON_CATEGORIES.keys())

def search_skins(query: str, weapon: str = None):
    """Search for skins matching a query"""
    results = []
    query_lower = query.lower()
    
    if weapon and weapon in WEAPON_SKINS:
        # Search within specific weapon
        for skin in WEAPON_SKINS[weapon]:
            if query_lower in skin.lower():
                results.append({
                    "weapon": weapon,
                    "skin": skin
                })
    else:
        # Search across all weapons
        for weapon_name, skins in WEAPON_SKINS.items():
            for skin in skins:
                if query_lower in skin.lower() or query_lower in weapon_name.lower():
                    results.append({
                        "weapon": weapon_name,
                        "skin": skin
                    })
    
    return results[:20]  # Limit results 