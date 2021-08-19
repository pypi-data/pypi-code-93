"""Contains impractical to obtain otherwise static data about NationStates.

I'd love to be able to request it from the API each time as opposed
to storing it, but NS makes it extremely difficult with the awkward
one-scale-at-a-time Census data interface.

I claim no ownership over the NationStates' content and really really
hope my usage of it can be considered Fair Use.
"""

from collections import namedtuple


__all__ = ('census_info', 'ScaleInfo')


happening_filters = {
    'law', 'change', 'dispatch', 'rmb', 'embassy', 'eject', 'admin',
    'move', 'founding', 'cte', 'vote', 'resolution', 'member', 'endo',
}


dispatch_categories = {
    'Factbook': {
        'Overview',
        'History',
        'Geography',
        'Culture',
        'Politics',
        'Legislation',
        'Religion',
        'Military',
        'Economy',
        'International',
        'Trivia',
        'Miscellaneous',
    },
    'Bulletin': {
        'Policy',
        'News',
        'Opinion',
        'Campaign',
    },
    'Account': {
        'Military',
        'Trade',
        'Sport',
        'Drama',
        'Diplomacy',
        'Science',
        'Culture',
        'Other',
    },
    'Meta': {
        'Gameplay',
        'Reference',
    },
}


_fields = ['id', 'title', 'ranked', 'measurement', 'image',
           'nation_description', 'region_description']
class ScaleInfo(namedtuple('ScaleInfo', _fields)):
    """Static information about a World Census scale.

    Attributes
    ----------
    id : int
        The scale id, an integer between 0 and 80 (84 if you also count
        Z-Day scales), inclusive.
    title : str
        The scale title.  For example, 'Civil Rights'.
    ranked : str
        A scale on which a nation or region is ranked, either in their
        region or the world.  For example, 'Most Extensive Civil
        Rights'.
    measurement : str
        The measurement scale.  For example, 'Martin Luther King, Jr.
        Units'.
    image : str
        An identifier NS uses for the Census tropy picture URLs.
    nation_description : str
        Description for nations.
    region_description : str
        Description for regions.
    """


census_info = [
    ScaleInfo(
        id=0,
        title='Civil Rights',
        ranked='Most Extensive Civil Rights',
        measurement='Martin Luther King, Jr. Units',
        image='liberal',
        nation_description=('The citizens of nations ranked highly enjoy a '
                            'great amount of civil rights, or freedoms to '
                            'go about their personal business without '
                            'interference or regulation from government.'),
        region_description=('The citizens of regions ranked highly enjoy a '
                            'great amount of civil rights, or freedoms to '
                            'go about their personal business without '
                            'interference or regulation from government.'),
    ),
    ScaleInfo(
        id=1,
        title='Economy',
        ranked='Most Efficient Economies',
        measurement='Krugman-Greenspan Business Outlook Index',
        image='economy',
        nation_description=('Nations ranked highly are the most ruthlessly '
                            'efficient at translating raw resources, '
                            'including people, into economic output.'),
        region_description=('Regions ranked highly are the most ruthlessly '
                            'efficient at translating raw resources, '
                            'including people, into economic output.'),
    ),
    ScaleInfo(
        id=2,
        title='Political Freedom',
        ranked='Most Politically Free',
        measurement='Diebold Election Inking Scale',
        image='polifree',
        nation_description=('These nations allow citizens the greatest '
                            'amount of freedom to select their own '
                            'government.'),
        region_description=('These regions allow citizens the greatest '
                            'amount of freedom to select their own '
                            'government.'),
    ),
    ScaleInfo(
        id=3,
        title='Population',
        ranked='Largest Populations',
        measurement='Capita',
        image='population',
        nation_description=('The following nations have the greatest '
                            'number of citizens.'),
        region_description=('The following regions have the most citizens '
                            'per nation.'),
    ),
    ScaleInfo(
        id=4,
        title='Wealth Gaps',
        ranked='Greatest Rich-Poor Divides',
        measurement='Rich To Poor Income Ratio',
        image='wealthgaps',
        nation_description=('Nations ranked highly have large gaps between '
                            'the incomes of rich and poor citizens. '
                            'Nations low on the list have high levels of '
                            'income equality.'),
        region_description=('Regions ranked highly have large gaps between '
                            'the incomes of rich and poor citizens. '
                            'Regions low on the list have high levels of '
                            'income equality.'),
    ),
    ScaleInfo(
        id=5,
        title='Death Rate',
        ranked='Highest Unexpected Death Rate',
        measurement='Bus Surprisal Index',
        image='death',
        nation_description=('The World Census paid their respects at '
                            'cemeteries in order to determine how likely '
                            'citizens were to die each year from unnatural '
                            'causes, such as crime, preventable illness, '
                            'accident, and government encouragement.'),
        region_description=('The World Census paid their respects at '
                            'cemeteries in order to determine how likely '
                            'citizens were to die each year from unnatural '
                            'causes, such as crime, preventable illness, '
                            'accident, and government encouragement.'),
    ),
    ScaleInfo(
        id=6,
        title='Compassion',
        ranked='Most Compassionate Citizens',
        measurement='Kitten Softness Rating',
        image='compassionate',
        nation_description=('Exhaustive World Census tests involving '
                            'kittens revealed the following nations to be '
                            'the most compassionate.'),
        region_description=('Exhaustive World Census tests involving '
                            'kittens revealed the following regions to be '
                            'the most compassionate.'),
    ),
    ScaleInfo(
        id=7,
        title='Eco-Friendliness',
        ranked='Most Eco-Friendly Governments',
        measurement='Dolphin Recycling Awareness Index',
        image='eco-govt',
        nation_description=('The following governments spend the greatest '
                            'amounts on environmental issues. This may not '
                            'always be reflected in the quality of that '
                            "nation's environment."),
        region_description=('The following governments spend the greatest '
                            'amounts on environmental issues. This may not '
                            'always be reflected in the quality of that '
                            "region's environment."),
    ),
    ScaleInfo(
        id=8,
        title='Social Conservatism',
        ranked='Most Conservative',
        measurement='Bush-Santorum Dawning Terror Index',
        image='conservative',
        nation_description=('Citizens in nations ranked highly tend to '
                            'have greater restrictions placed on what they '
                            'may do in their personal lives, whether via '
                            'community values or government-imposed law.'),
        region_description=('Citizens in regions ranked highly tend to '
                            'have greater restrictions placed on what they '
                            'may do in their personal lives, whether via '
                            'community values or government-imposed law.'),
    ),
    ScaleInfo(
        id=9,
        title='Nudity',
        ranked='Nudest',
        measurement='Cheeks Per Square Mile',
        image='nude',
        nation_description=('After exhaustive surveys, the World Census '
                            'calculated which nations have the greatest '
                            'acreages of flesh on public display.'),
        region_description=('After exhaustive surveys, the World Census '
                            'calculated which regions have the greatest '
                            'acreages of flesh on public display.'),
    ),
    ScaleInfo(
        id=10,
        title='Industry: Automobile Manufacturing',
        ranked='Largest Automobile Manufacturing Sector',
        measurement='Henry Ford Productivity Index',
        image='auto',
        nation_description=('World Census analysts extensively tested '
                            'concept muscle cars in empty parking lots in '
                            'order to estimate which nations have the '
                            'largest auto industries.'),
        region_description=('World Census analysts extensively tested '
                            'concept muscle cars in empty parking lots in '
                            'order to estimate which regions have the '
                            'largest auto industries.'),
    ),
    ScaleInfo(
        id=11,
        title='Industry: Cheese Exports',
        ranked='Largest Cheese Export Sector',
        measurement='Mozzarella Productivity Index',
        image='cheese',
        nation_description=('Qualified World Census Cheese Masters nibbled '
                            'their way across the globe to determine which '
                            'nations have the most developed cheese '
                            'exports.'),
        region_description=('Qualified World Census Cheese Masters nibbled '
                            'their way across the globe to determine which '
                            'regions have the most developed cheese '
                            'exports.'),
    ),
    ScaleInfo(
        id=12,
        title='Industry: Basket Weaving',
        ranked='Largest Basket Weaving Sector',
        measurement='Hickory Productivity Index',
        image='basket',
        nation_description=('World Census agents infiltrated a variety of '
                            'out-of-the-way towns and festivals in order '
                            'to determine which nations have the most '
                            'developed Basket Weaving industries.'),
        region_description=('World Census agents infiltrated a variety of '
                            'out-of-the-way towns and festivals in order '
                            'to determine which regions have the most '
                            'developed Basket Weaving industries.'),
    ),
    ScaleInfo(
        id=13,
        title='Industry: Information Technology',
        ranked='Largest Information Technology Sector',
        measurement='Fann-Boi Productivity Index',
        image='tech',
        nation_description=('World Census staff compiled lists over Smart '
                            'Phone related traffic accidents to determine '
                            'which nations have the largest Information '
                            'Technology industries.'),
        region_description=('World Census staff compiled lists over Smart '
                            'Phone related traffic accidents to determine '
                            'which regions have the largest Information '
                            'Technology industries.'),
    ),
    ScaleInfo(
        id=14,
        title='Industry: Pizza Delivery',
        ranked='Largest Pizza Delivery Sector',
        measurement='Pepperoni Propulsion Productivity Index',
        image='pizza',
        nation_description=('World Census staff spent many nights '
                            'answering the front door in order to measure '
                            'which nations have the biggest Pizza Delivery '
                            'industries.'),
        region_description=('World Census staff spent many nights '
                            'answering the front door in order to measure '
                            'which regions have the biggest Pizza Delivery '
                            'industries.'),
    ),
    ScaleInfo(
        id=15,
        title='Industry: Trout Fishing',
        ranked='Largest Trout Fishing Sector',
        measurement='Nemo Depletion Efficiency Index',
        image='fish',
        nation_description=('The World Census conducted frenzied haggling '
                            'with fishmongers in order to determine which '
                            'nations have the largest fishing industries.'),
        region_description=('The World Census conducted frenzied haggling '
                            'with fishmongers in order to determine which '
                            'regions have the largest fishing industries.'),
    ),
    ScaleInfo(
        id=16,
        title='Industry: Arms Manufacturing',
        ranked='Largest Arms Manufacturing Sector',
        measurement='Charon Conveyancy Index',
        image='arms',
        nation_description=('World Census special forces intercepted '
                            'crates of smuggled weapons to determine which '
                            'nations have the largest arms industry.'),
        region_description=('World Census special forces intercepted '
                            'crates of smuggled weapons to determine which '
                            'regions have the largest arms industry.'),
    ),
    ScaleInfo(
        id=17,
        title='Sector: Agriculture',
        ranked='Largest Agricultural Sector',
        measurement='Mu-Bah-Daggs Productivity Index',
        image='agriculture',
        nation_description=('World Census bean-counters on horseback '
                            'guided herds of cattle to slaughter in order '
                            'to determine which nations have the largest '
                            'agricultural sectors.'),
        region_description=('World Census bean-counters on horseback '
                            'guided herds of cattle to slaughter in order '
                            'to determine which regions have the largest '
                            'agricultural sectors.'),
    ),
    ScaleInfo(
        id=18,
        title='Industry: Beverage Sales',
        ranked='Largest Soda Pop Sector',
        measurement='Addison-Fukk Productivity Rating',
        image='soda',
        nation_description=('The World Census recorded sales of fizzy '
                            'syrup water in order to determine which '
                            'nations have the largest beverage industries.'),
        region_description=('The World Census recorded sales of fizzy '
                            'syrup water in order to determine which '
                            'regions have the largest beverage industries.'),
    ),
    ScaleInfo(
        id=19,
        title='Industry: Timber Woodchipping',
        ranked='Largest Timber Woodchipping Industry',
        measurement='Tasmanian Pulp Environmental Export Index',
        image='timber',
        nation_description=('The World Census measured the rate of '
                            'desertification in order to calculate which '
                            'nations have the largest timber industry.'),
        region_description=('The World Census measured the rate of '
                            'desertification in order to calculate which '
                            'regions have the largest timber industry.'),
    ),
    ScaleInfo(
        id=20,
        title='Industry: Mining',
        ranked='Largest Mining Sector',
        measurement='Blue Sky Asbestos Index',
        image='mining',
        nation_description=('World Census experts measured the volume of '
                            'stuff removed from the ground to determine '
                            'which nations have the largest mining '
                            'industries.'),
        region_description=('World Census experts measured the volume of '
                            'stuff removed from the ground to determine '
                            'which regions have the largest mining '
                            'industries.'),
    ),
    ScaleInfo(
        id=21,
        title='Industry: Insurance',
        ranked='Largest Insurance Industry',
        measurement='Risk Expulsion Effectiveness Rating',
        image='insurance',
        nation_description=('The World Census posed as door-to-door '
                            'salespeople in order to establish which '
                            'nations have the most extensive Insurance '
                            'industries.'),
        region_description=('The World Census posed as door-to-door '
                            'salespeople in order to establish which '
                            'regions have the most extensive Insurance '
                            'industries.'),
    ),
    ScaleInfo(
        id=22,
        title='Industry: Furniture Restoration',
        ranked='Largest Furniture Restoration Industry',
        measurement='Spitz-Pollish Productivity Index',
        image='furniture',
        nation_description=('World Census analysts spend quiet weekends in '
                            'the countryside in order to determine which '
                            'nations have the largest Furniture '
                            'Restoration industries.'),
        region_description=('World Census analysts spend quiet weekends in '
                            'the countryside in order to determine which '
                            'regions have the largest Furniture '
                            'Restoration industries.'),
    ),
    ScaleInfo(
        id=23,
        title='Industry: Retail',
        ranked='Largest Retail Industry',
        measurement='Shrinkwrap Consignment Productivity Index',
        image='retail',
        nation_description=('The World Census estimated levels of employee '
                            'ennui to determine which nations have the '
                            'largest retail industries.'),
        region_description=('The World Census estimated levels of employee '
                            'ennui to determine which regions have the '
                            'largest retail industries.'),
    ),
    ScaleInfo(
        id=24,
        title='Industry: Book Publishing',
        ranked='Largest Publishing Industry',
        measurement='Bella Potter Productivity e-Index',
        image='publishing',
        nation_description=('The World Census tallied social media '
                            'complaints from students regarding overpriced '
                            'textbooks to determine which nations have the '
                            'largest book publishing industries.'),
        region_description=('The World Census tallied social media '
                            'complaints from students regarding overpriced '
                            'textbooks to determine which regions have the '
                            'largest book publishing industries.'),
    ),
    ScaleInfo(
        id=25,
        title='Industry: Gambling',
        ranked='Largest Gambling Industry',
        measurement='Kelly Criterion Productivity Index',
        image='gambling',
        nation_description=('The World Census tailed known underworld '
                            'figures in order to determine which nations '
                            'have the largest gambling industries.'),
        region_description=('The World Census tailed known underworld '
                            'figures in order to determine which regions '
                            'have the largest gambling industries.'),
    ),
    ScaleInfo(
        id=26,
        title='Sector: Manufacturing',
        ranked='Largest Manufacturing Sector',
        measurement='Gooback-Jerbs Productivity Index',
        image='manufacturing',
        nation_description=('World Census bean-counters tabulated data '
                            'from across several industries in order to '
                            'determine which nations have the largest '
                            'Manufacturing sectors.'),
        region_description=('World Census bean-counters tabulated data '
                            'from across several industries in order to '
                            'determine which regions have the largest '
                            'Manufacturing sectors.'),
    ),
    ScaleInfo(
        id=27,
        title='Government Size',
        ranked='Largest Governments',
        measurement='Bureaucratic Comprehensiveness Rating Scale Index',
        image='govt',
        nation_description=('World Census agents lined up at public '
                            'agencies around the world in order to study '
                            'the extent of government in nations, taking '
                            'into consideration economic output, social '
                            'and cultural significance, and raw size.'),
        region_description=('World Census agents lined up at public '
                            'agencies around the world in order to study '
                            'the extent of government in regions, taking '
                            'into consideration economic output, social '
                            'and cultural significance, and raw size.'),
    ),
    ScaleInfo(
        id=28,
        title='Welfare',
        ranked='Largest Welfare Programs',
        measurement='Safety Net Mesh Density Rating',
        image='welfare',
        nation_description=('Governments ranked highly spend the most on '
                            'social welfare programs. Nations ranked low '
                            'tend to have weak or non-existent government '
                            'welfare.'),
        region_description=('Governments ranked highly spend the most on '
                            'social welfare programs. Regions ranked low '
                            'tend to have weak or non-existent government '
                            'welfare.'),
    ),
    ScaleInfo(
        id=29,
        title='Public Healthcare',
        ranked='Most Extensive Public Healthcare',
        measurement='Theresa-Nightingale Rating',
        image='healthcare',
        nation_description=('World Census interns were infected with '
                            'obscure diseases in order to test which '
                            'nations had the most effective and '
                            'well-funded public healthcare facilities.'),
        region_description=('World Census interns were infected with '
                            'obscure diseases in order to test which '
                            'regions had the most effective and '
                            'well-funded public healthcare facilities.'),
    ),
    ScaleInfo(
        id=30,
        title='Law Enforcement',
        ranked='Most Advanced Law Enforcement',
        measurement='Orwell Orderliness Index',
        image='police',
        nation_description=('World Census interns were framed for minor '
                            'crimes in order to measure the response '
                            'times, effectiveness, and amount of firepower '
                            'deployed by the law enforcement agencies of '
                            'different nations.'),
        region_description=('World Census interns were framed for minor '
                            'crimes in order to measure the response '
                            'times, effectiveness, and amount of firepower '
                            'deployed by the law enforcement agencies of '
                            'different regions.'),
    ),
    ScaleInfo(
        id=31,
        title='Business Subsidization',
        ranked='Most Subsidized Industry',
        measurement='Gilded Widget Scale',
        image='business',
        nation_description=('Nations ranked highly spend the most on '
                            'developing and supporting industry, a '
                            "practice known as 'corporate welfare.'"),
        region_description=('Regions ranked highly spend the most on '
                            'developing and supporting industry, a '
                            "practice known as 'corporate welfare.'"),
    ),
    ScaleInfo(
        id=32,
        title='Religiousness',
        ranked='Most Devout',
        measurement='Prayers Per Hour',
        image='devout',
        nation_description=('World Census Inquisitors conducted rigorous '
                            'one-on-one interviews probing the depth of '
                            "citizens' beliefs in order to determine which "
                            'nations were the most devout.'),
        region_description=('World Census Inquisitors conducted rigorous '
                            'one-on-one interviews probing the depth of '
                            "citizens' beliefs in order to determine which "
                            'regions were the most devout.'),
    ),
    ScaleInfo(
        id=33,
        title='Income Equality',
        ranked='Most Income Equality',
        measurement='Marx-Engels Emancipation Scale',
        image='equality',
        nation_description=('World Census boffins calculated the '
                            'difference in incomes between the richest and '
                            'poorest citizens, where a score of 50 would '
                            'mean that poor incomes are 50% of rich '
                            'incomes.'),
        region_description=('World Census boffins calculated the '
                            'difference in incomes between the richest and '
                            'poorest citizens, where a score of 50 would '
                            'mean that poor incomes are 50% of rich '
                            'incomes.'),
    ),
    ScaleInfo(
        id=34,
        title='Niceness',
        ranked='Nicest Citizens',
        measurement='Average Smiles Per Day',
        image='nice',
        nation_description=('World Census sociology experts studied '
                            'citizens from various nations to determine '
                            'which seemed most friendly and concerned for '
                            'others.'),
        region_description=('World Census sociology experts studied '
                            'citizens from various regions to determine '
                            'which seemed most friendly and concerned for '
                            'others.'),
    ),
    ScaleInfo(
        id=35,
        title='Rudeness',
        ranked='Rudest Citizens',
        measurement='Insults Per Minute',
        image='rude',
        nation_description=('World Census experts telephoned citizens from '
                            'all nations at just before dinner time, in a '
                            'study to determine which populations were '
                            'most brash, rude, or brusque.'),
        region_description=('World Census experts telephoned citizens from '
                            'all regions at just before dinner time, in a '
                            'study to determine which populations were '
                            'most brash, rude, or brusque.'),
    ),
    ScaleInfo(
        id=36,
        title='Intelligence',
        ranked='Smartest Citizens',
        measurement='Quips Per Hour',
        image='smart',
        nation_description=('The World Census eavesdropped on '
                            'conversations in coffee shops, on campuses, '
                            'and around cinemas in order to determine '
                            'which nations have the most quick-witted, '
                            'insightful, and knowledgeable citizens.'),
        region_description=('The World Census eavesdropped on '
                            'conversations in coffee shops, on campuses, '
                            'and around cinemas in order to determine '
                            'which regions have the most quick-witted, '
                            'insightful, and knowledgeable citizens.'),
    ),
    ScaleInfo(
        id=37,
        title='Ignorance',
        ranked='Most Ignorant Citizens',
        measurement='Missed References Per Hour',
        image='stupid',
        nation_description=('The World Census studied which nations seemed '
                            'to have the greatest numbers of citizens that '
                            'fell into the categories "ignorant," '
                            '"oblivious," or "just plain dumb."'),
        region_description=('The World Census studied which regions seemed '
                            'to have the greatest numbers of citizens that '
                            'fell into the categories "ignorant," '
                            '"oblivious," or "just plain dumb."'),
    ),
    ScaleInfo(
        id=38,
        title='Political Apathy',
        ranked='Most Politically Apathetic Citizens',
        measurement='Whatever',
        image='apathetic',
        nation_description=('These results were determined by seeing how '
                            'many citizens of each nation answered a '
                            'recent World Census survey on the local '
                            'political situation by ticking the "Don\'t '
                            'Give a Damn" box.'),
        region_description=('These results were determined by seeing how '
                            'many citizens of each region answered a '
                            'recent World Census survey on the local '
                            'political situation by ticking the "Don\'t '
                            'Give a Damn" box.'),
    ),
    ScaleInfo(
        id=39,
        title='Health',
        ranked='Healthiest Citizens',
        measurement='Bananas Ingested Per Day',
        image='healthy',
        nation_description=('A measure of the general physical health of '
                            'citizens in each nation.'),
        region_description=('A measure of the general physical health of '
                            'citizens in each region.'),
    ),
    ScaleInfo(
        id=40,
        title='Cheerfulness',
        ranked='Most Cheerful Citizens',
        measurement='Percentage Of Water Glasses Perceived Half-Full',
        image='happy',
        nation_description=('The World Census shared cheeky grins with '
                            'citizens around the world in order to '
                            'determine which were the most relentlessly '
                            'cheerful.'),
        region_description=('The World Census shared cheeky grins with '
                            'citizens around the world in order to '
                            'determine which were the most relentlessly '
                            'cheerful.'),
    ),
    ScaleInfo(
        id=41,
        title='Weather',
        ranked='Best Weather',
        measurement='Meters Of Sunlight',
        image='weather',
        nation_description=('The following nations were determined to have '
                            'the best all-round weather.'),
        region_description=('The following regions were determined to have '
                            'the best all-round weather.'),
    ),
    ScaleInfo(
        id=42,
        title='Compliance',
        ranked='Lowest Crime Rates',
        measurement='Law-abiding Acts Per Hour',
        image='lowcrime',
        nation_description=('World Census agents attempted to lure '
                            'citizens into committing various crimes in '
                            'order to test the reluctance of citizens to '
                            'break the law.'),
        region_description=('World Census agents attempted to lure '
                            'citizens into committing various crimes in '
                            'order to test the reluctance of citizens to '
                            'break the law.'),
    ),
    ScaleInfo(
        id=43,
        title='Safety',
        ranked='Safest',
        measurement='Bubble-Rapp Safety Rating',
        image='safe',
        nation_description=('World Census agents tested the sharpness of '
                            "household objects, the softness of children's "
                            'play equipment, and the survival rate of '
                            'people taking late walks to determine how '
                            'safe each nation is to visit.'),
        region_description=('World Census agents tested the sharpness of '
                            "household objects, the softness of children's "
                            'play equipment, and the survival rate of '
                            'people taking late walks to determine how '
                            'safe each region is to visit.'),
    ),
    ScaleInfo(
        id=44,
        title='Lifespan',
        ranked='Longest Average Lifespans',
        measurement='Years',
        image='life',
        nation_description=('Nations ranked highly have lower rates of '
                            'preventable death, with their citizens '
                            'enjoying longer average lifespans.'),
        region_description=('Regions ranked highly have lower rates of '
                            'preventable death, with their citizens '
                            'enjoying longer average lifespans.'),
    ),
    ScaleInfo(
        id=45,
        title='Ideological Radicality',
        ranked='Most Extreme',
        measurement='Paul-Nader Subjective Decentrality Index',
        image='extreme',
        nation_description=('The World Census ranked nations on the basis '
                            'of how odd, extreme, or fundamentalist their '
                            'social, economic, and political systems are.'),
        region_description=('The World Census ranked regions on the basis '
                            'of how odd, extreme, or fundamentalist their '
                            'social, economic, and political systems are.'),
    ),
    ScaleInfo(
        id=46,
        title='Defense Forces',
        ranked='Most Advanced Defense Forces',
        measurement='Total War Preparedness Rating',
        image='defense',
        nation_description=('Nations ranked highly spend the most on '
                            'national defense, and are most secure against '
                            'foreign aggression.'),
        region_description=('Regions ranked highly spend the most on '
                            'regional defense, and are most secure against '
                            'foreign aggression.'),
    ),
    ScaleInfo(
        id=47,
        title='Pacifism',
        ranked='Most Pacifist',
        measurement='Cheeks Turned Per Day',
        image='peace',
        nation_description=('Nations ranked highly pursue diplomatic '
                            'solutions rather than military ones in the '
                            'international arena, have small or '
                            'nonexistent militaries, and peace-loving '
                            'citizens.'),
        region_description=('Regions ranked highly pursue diplomatic '
                            'solutions rather than military ones in the '
                            'international arena, have small or '
                            'nonexistent militaries, and peace-loving '
                            'citizens.'),
    ),
    ScaleInfo(
        id=48,
        title='Economic Freedom',
        ranked='Most Pro-Market',
        measurement='Rand Index',
        image='pro-market',
        nation_description=('This data was compiled by surveying a random '
                            'sample of businesses with the question, "Do '
                            'you believe the government is committed to '
                            'free market policies?"'),
        region_description=('This data was compiled by surveying a random '
                            'sample of businesses with the question, "Do '
                            'you believe the government is committed to '
                            'free market policies?"'),
    ),
    ScaleInfo(
        id=49,
        title='Taxation',
        ranked='Highest Average Tax Rates',
        measurement='Effective Tax Rate',
        image='hightax',
        nation_description=('Although some nations have a flat tax rate '
                            'for all citizens while others tax the rich '
                            'more heavily than the poor, the World Census '
                            "used averages to rank the world's most taxing "
                            'governments.'),
        region_description=('Although some regions have a flat tax rate '
                            'for all citizens while others tax the rich '
                            'more heavily than the poor, the World Census '
                            "used averages to rank the world's most taxing "
                            'governments.'),
    ),
    ScaleInfo(
        id=50,
        title='Freedom From Taxation',
        ranked='Lowest Overall Tax Burden',
        measurement='Hayek Index',
        image='lowtax',
        nation_description=('World Census financial experts assessed '
                            'nations across a range of direct and indirect '
                            'measures in order to determine which placed '
                            'the lowest tax burden on their citizens.'),
        region_description=('World Census financial experts assessed '
                            'regions across a range of direct and indirect '
                            'measures in order to determine which placed '
                            'the lowest tax burden on their citizens.'),
    ),
    ScaleInfo(
        id=51,
        title='Corruption',
        ranked='Most Corrupt Governments',
        measurement='Kickbacks Per Hour',
        image='corrupt',
        nation_description=('World Census officials visited a range of '
                            'government departments and recorded how '
                            'frequently bribes were required to complete '
                            'simple administrative requests.'),
        region_description=('World Census officials visited a range of '
                            'government departments and recorded how '
                            'frequently bribes were required to complete '
                            'simple administrative requests.'),
    ),
    ScaleInfo(
        id=52,
        title='Integrity',
        ranked='Least Corrupt Governments',
        measurement='Percentage Of Bribes Refused',
        image='leastcorrupt',
        nation_description=('World Census agents tempted government '
                            'officials with financial and other '
                            'inducements to bend the rules and recorded '
                            'how often their proposals were declined.'),
        region_description=('World Census agents tempted government '
                            'officials with financial and other '
                            'inducements to bend the rules and recorded '
                            'how often their proposals were declined.'),
    ),
    ScaleInfo(
        id=53,
        title='Authoritarianism',
        ranked='Most Authoritarian',
        measurement='milliStalins',
        image='authoritarian',
        nation_description=('World Census staff loitered innocuously in '
                            'various public areas and recorded the length '
                            'of time that passed before they were '
                            'approached by dark-suited officials.'),
        region_description=('World Census staff loitered innocuously in '
                            'various public areas and recorded the length '
                            'of time that passed before they were '
                            'approached by dark-suited officials.'),
    ),
    ScaleInfo(
        id=54,
        title='Youth Rebelliousness',
        ranked='Most Rebellious Youth',
        measurement='Stark-Dean Displacement Index',
        image='rebelyouth',
        nation_description=('World Census observers counted the number of '
                            'times their car stereo was stolen from '
                            'outside fast food stores to determine which '
                            'nations have relatively high levels of '
                            'youth-related crime.'),
        region_description=('World Census observers counted the number of '
                            'times their car stereo was stolen from '
                            'outside fast food stores to determine which '
                            'regions have relatively high levels of '
                            'youth-related crime.'),
    ),
    ScaleInfo(
        id=55,
        title='Culture',
        ranked='Most Cultured',
        measurement='Snufflebottom-Wiggendum Pentatonic Scale',
        image='culture',
        nation_description=('After spending many tedious hours in coffee '
                            'shops and concert halls, World Census experts '
                            'have found the following nations to be the '
                            'most cultured.'),
        region_description=('After spending many tedious hours in coffee '
                            'shops and concert halls, World Census experts '
                            'have found the following regions to be the '
                            'most cultured.'),
    ),
    ScaleInfo(
        id=56,
        title='Employment',
        ranked='Highest Workforce Participation Rate',
        measurement='Workforce Participation Rate',
        image='employed',
        nation_description=('World Census experts studied the ratings of '
                            'daytime television chat shows to estimate the '
                            'percentage of citizens who are employed.'),
        region_description=('World Census experts studied the ratings of '
                            'daytime television chat shows to estimate the '
                            'percentage of citizens who are employed.'),
    ),
    ScaleInfo(
        id=57,
        title='Public Transport',
        ranked='Most Advanced Public Transport',
        measurement='Societal Mobility Rating',
        image='publictransport',
        nation_description=('World Census experts captured, tagged, and '
                            'released trains in order to identify which '
                            'nations have the most extensive, well-funded '
                            'public transportation systems.'),
        region_description=('World Census experts captured, tagged, and '
                            'released trains in order to identify which '
                            'regions have the most extensive, well-funded '
                            'public transportation systems.'),
    ),
    ScaleInfo(
        id=58,
        title='Tourism',
        ranked='Most Popular Tourist Destinations',
        measurement='Tourists Per Hour',
        image='tourism',
        nation_description=('World Census experts tracked millions of '
                            'international tourists in order to determine '
                            "the world's favourite nations to sight-see."),
        region_description=('World Census experts tracked millions of '
                            'international tourists in order to determine '
                            "the world's favourite regions to sight-see."),
    ),
    ScaleInfo(
        id=59,
        title='Weaponization',
        ranked='Most Armed',
        measurement='Weapons Per Person',
        image='armed',
        nation_description=('World Census experts took their lives into '
                            'their hands in order to ascertain the average '
                            'number of deadly weapons per citizen.'),
        region_description=('World Census experts took their lives into '
                            'their hands in order to ascertain the average '
                            'number of deadly weapons per citizen.'),
    ),
    ScaleInfo(
        id=60,
        title='Recreational Drug Use',
        ranked='Highest Drug Use',
        measurement='Pineapple Fondness Rating',
        image='drugs',
        nation_description=('World Census experts sampled many cakes of '
                            "dubious content to determine which nations' "
                            'citizens consume the most recreational drugs.'),
        region_description=('World Census experts sampled many cakes of '
                            "dubious content to determine which regions' "
                            'citizens consume the most recreational drugs.'),
    ),
    ScaleInfo(
        id=61,
        title='Obesity',
        ranked='Fattest Citizens',
        measurement='Obesity Rate',
        image='fat',
        nation_description=('World Census takers tracked the sale of '
                            'Cheetos and Twinkies to ascertain which '
                            'nations most enjoyed the "kind bud."'),
        region_description=('World Census takers tracked the sale of '
                            'Cheetos and Twinkies to ascertain which '
                            'regions most enjoyed the "kind bud."'),
    ),
    ScaleInfo(
        id=62,
        title='Secularism',
        ranked='Most Secular',
        measurement='Atheism Rate',
        image='godforsaken',
        nation_description=('World Census experts studied which citizens '
                            'seemed least concerned about eternal '
                            'damnation, spiritual awakeness, and chakra '
                            'wellbeing in order to determine the most '
                            'godforsaken nations.'),
        region_description=('World Census experts studied which citizens '
                            'seemed least concerned about eternal '
                            'damnation, spiritual awakeness, and chakra '
                            'wellbeing in order to determine the most '
                            'godforsaken regions.'),
    ),
    ScaleInfo(
        id=63,
        title='Environmental Beauty',
        ranked='Most Beautiful Environments',
        measurement='Pounds Of Wildlife Per Square Mile',
        image='environment',
        nation_description=('World Census researchers spent many arduous '
                            'weeks lying on beaches and trekking through '
                            'rainforests to compile a definitive list of '
                            'the most attractive and best cared for '
                            'environments.'),
        region_description=('World Census researchers spent many arduous '
                            'weeks lying on beaches and trekking through '
                            'rainforests to compile a definitive list of '
                            'the most attractive and best cared for '
                            'environments.'),
    ),
    ScaleInfo(
        id=64,
        title='Charmlessness',
        ranked='Most Avoided',
        measurement='Kardashian Reflex Score',
        image='avoided',
        nation_description=('Nations ranked highly are considered by many '
                            'to be the most inhospitable, charmless, and '
                            'ghastly places to spend a vacation, or, '
                            'indeed, any time at all.'),
        region_description=('Regions ranked highly are considered by many '
                            'to be the most inhospitable, charmless, and '
                            'ghastly places to spend a vacation, or, '
                            'indeed, any time at all.'),
    ),
    ScaleInfo(
        id=65,
        title='Influence',
        ranked='Most Influential',
        measurement='Soft Power Disbursement Rating',
        image='influence',
        nation_description=('World Census experts spent many evenings '
                            'loitering in the corridors of power in order '
                            'to determine which nations were the greatest '
                            'international diplomacy heavyweights.'),
        region_description=('World Census experts spent many evenings '
                            'loitering in the corridors of power in order '
                            'to determine which regions were the greatest '
                            'international diplomacy heavyweights.'),
    ),
    ScaleInfo(
        id=66,
        title='World Assembly Endorsements',
        ranked='Most World Assembly Endorsements',
        measurement='Valid Endorsements',
        image='endorsed',
        nation_description=('World Census staff pored through World '
                            'Assembly records to determine which nations '
                            'were the most endorsed by others in their '
                            'region.'),
        region_description=('World Census staff pored through World '
                            'Assembly records to determine the average '
                            'number of endorsements per nation in each '
                            'region.'),
    ),
    ScaleInfo(
        id=67,
        title='Averageness',
        ranked='Most Average',
        measurement='Average Standardized Normality Scale',
        image='average',
        nation_description=('World Census staff took time out to pay '
                            'tribute to those most overlooked of nations: '
                            'the determinedly average.'),
        region_description=('World Census staff took time out to pay '
                            'tribute to those most overlooked of regions: '
                            'the determinedly average.'),
    ),
    ScaleInfo(
        id=68,
        title='Human Development Index',
        ranked='Most Developed',
        measurement='Human Development Index',
        image='hdi',
        nation_description=('The World Census compiles a "Human '
                            'Development Index" by measuring citizens\' '
                            'average life expectancy, education, and '
                            'income.'),
        region_description=('The World Census compiles a "Human '
                            'Development Index" by measuring citizens\' '
                            'average life expectancy, education, and '
                            'income.'),
    ),
    ScaleInfo(
        id=69,
        title='Primitiveness',
        ranked='Most Primitive',
        measurement='Scary Big Number Scale',
        image='primitive',
        nation_description=('Nations were ranked by World Census officials '
                            'based on the number of natural phenomena '
                            'attributed to the unknowable will of '
                            'animal-based spirit gods.'),
        region_description=('Regions were ranked by World Census officials '
                            'based on the number of natural phenomena '
                            'attributed to the unknowable will of '
                            'animal-based spirit gods.'),
    ),
    ScaleInfo(
        id=70,
        title='Scientific Advancement',
        ranked='Most Scientifically Advanced',
        measurement='Kurzweil Singularity Index',
        image='advanced',
        nation_description=('World Census researchers quantified national '
                            'scientific advancement by quizzing random '
                            'citizens about quantum chromodynamics, '
                            'space-time curvature and stem cell '
                            'rejuvenation therapies. Responses based on '
                            'Star Trek were discarded.'),
        region_description=('World Census researchers quantified regional '
                            'scientific advancement by quizzing random '
                            'citizens about quantum chromodynamics, '
                            'space-time curvature and stem cell '
                            'rejuvenation therapies. Responses based on '
                            'Star Trek were discarded.'),
    ),
    ScaleInfo(
        id=71,
        title='Inclusiveness',
        ranked='Most Inclusive',
        measurement='Mandela-Wollstonecraft Non-Discrimination Index',
        image='inclusive',
        nation_description=('WA analysts ranked nations based on whether '
                            'all citizens were commonly treated as equally '
                            'valuable members of society.'),
        region_description=('WA analysts ranked regions based on whether '
                            'all citizens were commonly treated as equally '
                            'valuable members of society.'),
    ),
    ScaleInfo(
        id=72,
        title='Average Income',
        ranked='Highest Average Incomes',
        measurement='Standard Monetary Units',
        image='income',
        nation_description=('The World Census carefully compared the '
                            'average spending power of citizens in each '
                            'nation.'),
        region_description=('The World Census carefully compared the '
                            'average spending power of citizens in each '
                            'region.'),
    ),
    ScaleInfo(
        id=73,
        title='Average Income of Poor',
        ranked='Highest Poor Incomes',
        measurement='Standard Monetary Units',
        image='poorincome',
        nation_description=('The World Census studied the spending power '
                            'of the poorest 10% of citizens in each nation.'),
        region_description=('The World Census studied the spending power '
                            'of the poorest 10% of citizens in each region.'),
    ),
    ScaleInfo(
        id=74,
        title='Average Income of Rich',
        ranked='Highest Wealthy Incomes',
        measurement='Standard Monetary Units',
        image='richincome',
        nation_description=('The World Census studied the spending power '
                            'of the richest 10% of citizens in each nation.'),
        region_description=('The World Census studied the spending power '
                            'of the richest 10% of citizens in each region.'),
    ),
    ScaleInfo(
        id=75,
        title='Public Education',
        ranked='Most Advanced Public Education',
        measurement='Edu-tellignce\u00AE Test Score',
        image='educated',
        nation_description=('Fresh-faced World Census agents infiltrated '
                            'schools with varying degrees of success in '
                            'order to determine which nations had the most '
                            'widespread, well-funded, and advanced public '
                            'education programs.'),
        region_description=('Fresh-faced World Census agents infiltrated '
                            'schools with varying degrees of success in '
                            'order to determine which regions had the most '
                            'widespread, well-funded, and advanced public '
                            'education programs.'),
    ),
    ScaleInfo(
        id=76,
        title='Economic Output',
        ranked='Highest Economic Output',
        measurement='Standard Monetary Units',
        image='gdp',
        nation_description=('World Census bean-counters crunched the '
                            'numbers to calculate national Gross Domestic '
                            'Product. Older nations, with higher '
                            'populations, were noted to have a distinct '
                            'advantage.'),
        region_description=('World Census bean-counters crunched the '
                            'numbers to calculate regional Gross Domestic '
                            'Product. Older regions, with higher '
                            'populations, were noted to have a distinct '
                            'advantage.'),
    ),
    ScaleInfo(
        id=77,
        title='Crime',
        ranked='Highest Crime Rates',
        measurement='Crimes Per Hour',
        image='crime',
        nation_description=('World Census interns were dispatched to seedy '
                            'back alleys in order to determine which '
                            'nations have the highest crime rates.'),
        region_description=('World Census interns were dispatched to seedy '
                            'back alleys in order to determine which '
                            'regions have the highest crime rates.'),
    ),
    ScaleInfo(
        id=78,
        title='Foreign Aid',
        ranked='Highest Foreign Aid Spending',
        measurement='Clooney Contribution Index',
        image='aid',
        nation_description=('The World Census intercepted food drops in '
                            'several war-torn regions to determine which '
                            'nations spent the most on international aid. '),
        region_description=('The World Census intercepted food drops in '
                            'several war-torn regions to determine which '
                            'regions spent the most on international aid. '),
    ),
    ScaleInfo(
        id=79,
        title='Black Market',
        ranked='Largest Black Market',
        measurement='Standard Monetary Units',
        image='blackmarket',
        nation_description=('World Census agents tracked "off the books" '
                            'deals and handshake agreements in order to '
                            "study the size of nations' informal economies."),
        region_description=('World Census agents tracked "off the books" '
                            'deals and handshake agreements in order to '
                            "study the size of regions' informal economies."),
    ),
    ScaleInfo(
        id=80,
        title='Residency',
        ranked='Most Stationary',
        measurement='Days',
        image='stationary',
        nation_description=('Long-term World Census surveillance revealed '
                            'which nations have been resident in their '
                            'current region for the longest time.'),
        region_description=('Long-term World Census surveillance revealed '
                            'which regions have the most physically '
                            'grounded nations.'),
    ),

    # Z-Day scales:

    ScaleInfo(
        id=81,
        title='Survivors',
        ranked='Most Survivors',
        measurement='Capita',
        image='survivors',
        nation_description=('The following nations have the greatest '
                            'number of surviving citizens.'),
        region_description=('The following regions have the most survivors '
                            'per nation.'),
    ),
    ScaleInfo(
        id=82,
        title='Zombies',
        ranked='Most Zombies',
        measurement='Capita',
        image='zombies',
        nation_description=('The following nations have the greatest '
                            'number of zombified citizens.'),
        region_description=('The following regions have the most zombies '
                            'per nation.'),
    ),
    ScaleInfo(
        id=83,
        title='Dead',
        ranked='Most Dead',
        measurement='Capita',
        image='dead',
        nation_description=('The following nations have the greatest '
                            'number of dead citizens.'),
        region_description=('The following regions have the most dead per '
                            'nation.'),
    ),
    ScaleInfo(
        id=84,
        title='Percentage Zombies',
        ranked='Most Zombified',
        measurement='Romero-Brooks Index',
        image='zratio',
        nation_description=('The following nations have the highest '
                            'fraction of zombies among the animate.'),
        region_description=('The following regions have the most zombies '
                            'per survivor per nation.'),
    ),
    ScaleInfo(
        id=85,
        title='Average Disposable Income',
        ranked='Highest Disposable Incomes',
        measurement='Standard Monetary Units',
        image='dispincome',
        nation_description=('The World Census calculated the average incomes '
                            'of citizens after paying tax.'),
        region_description=('The World Census calculated the average incomes '
                            'of citizens after paying tax.'),
    ),
    ScaleInfo(
        id=86,
        title='International Artwork',
        ranked='Most Valuable International Artwork',
        measurement='Bank',
        image='deck',
        nation_description=('Some nations attempt to collect signature'
                            ' artworks of other nations, developing'
                            ' collections known as "decks." The World Census'
                            ' has estimated their value.'),
        region_description=('Some regions attempt to collect signature'
                            ' artworks of other regions, developing'
                            ' collections known as "decks." The World Census'
                            ' has estimated their value.'),
    ),
    ScaleInfo(
        id=87,
        title='Patriotism',
        ranked='Most Patriotic',
        measurement='flags saluted per person per day',
        image='patriotism',
        nation_description=('World Census data collectors measured the fervor'
                            ' with which citizens believed their own nation'
                            ' was the greatest of all.'),
        region_description=('World Census data collectors measured the fervor'
                            ' with which citizens believed their own region'
                            ' was the greatest of all.'),
    ),
    ScaleInfo(
        id=88,
        title='Food Quality',
        ranked='Highest Food Quality',
        measurement='Meeshlin-Starr Index',
        image='foodquality',
        nation_description=('Professional food critics dined out at'
                            ' restaurants and popped into home kitchens to'
                            ' judge ingredient quality, creativity, and'
                            ' diversity of food.'),
        region_description=('Professional food critics dined out at'
                            ' restaurants and popped into home kitchens to'
                            ' judge ingredient quality, creativity, and'
                            ' diversity of food.'),
    ),
]
