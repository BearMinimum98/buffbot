class Data:
	"Stores all the config for BuffBot. Add in buffs by adding in entries to buffs. Use all lowercase for the key name, and make sure id is a string, not int"
	secretKey = "secretkey"
	USERNAME = "username"
	PASSWORD = "password"
	ACCORDION_DURATION = 20
	MAXLENGTH = 100
	MPCOSTREDUCTION = 3

	buffs = {
		"the moxious madrigal": {
			"id": "6004",
			"mp": 2,
			"available": True
		},
		"the magical mojomuscular melody": {
			"id": "6007",
			"mp": 3,
			"available": True
		},
		"cletus's canticle of celerity": {
			"id": "6005",
			"mp": 4,
			"available": True
		},
		"the power ballad of the arrowsmith": {
			"id": "6008",
			"mp": 5,
			"available": True
		},
		"the polka of plenty": {
			"id": "6006",
			"mp": 7,
			"available": True
		},
		"jackasses' symphony of destruction": {
			"id": "6012",
			"mp": 9,
			"available": True
		},
		"fat leon's phat loot lyric": {
			"id": "6010",
			"mp": 11,
			"available": True
		},
		"brawnee's anthem of absorption": {
			"id": "6009",
			"mp": 13,
			"available": True
		},
		"the psalm of pointiness": {
			"id": "6011",
			"mp": 15,
			"available": True
		},
		"stevedave's shanty of superiority": {
			"id": "6013",
			"mp": 30,
			"available": True
		},
		"aloysius' antiphon of aptitude": {
			"id": "6003",
			"mp": 40,
			"available": True
		},
		"the ode to booze": {
			"id": "6014",
			"mp": 50,
			"available": True
		},
		"the sonata of sneakiness": {
			"id": "6015",
			"mp": 20,
			"available": True
		},
		"carlweather's cantata of confrontation": {
			"id": "6016",
			"mp": 20,
			"available": True
		},
		"ur-kel's aria of annoyance": {
			"id": "6017",
			"mp": 30,
			"available": False
		},
		"dirge of dreadfulness": {
			"id": "6018",
			"mp": 9,
			"available": True
		},
		"inigo's incantation of inspiration": {
			"id": "6028",
			"mp": 100,
			"available": True,
			"once": True
		},
		"donho's bubbly ballad": {
			"id": "6026",
			"mp": 75,
			"available": True
		}
}