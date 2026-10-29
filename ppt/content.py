"""Single source of slide text + speaker script (used by the PPT and the PDF guide)."""

SLIDES = [
    dict(kicker="BDSMA MICRO PROJECT", title="SkyTrace",
         sub="Studying the paths of flights over India using Big Data tools",
         bullets=["Topic: Flight Trajectory Analysis (spatio-temporal analytics)",
                  "Tools: Hadoop, MapReduce, Spark, MongoDB, Graph analysis",
                  "Linked to UN SDG 9: Industry, Innovation & Infrastructure"],
         notes="Good morning. Our micro project is called SkyTrace. In simple words, we take the location data "
               "that every aeroplane sends out, store it with big data tools like Hadoop, and study it to find "
               "where the sky over India is crowded, which flights take longer paths than needed, and which "
               "airports are the most important. This connects to the UN Sustainable Development Goal 9, "
               "which is about building good infrastructure."),
    dict(kicker="INTRODUCTION", title="What is this project?",
         bullets=["Every plane sends its position every few seconds, like a GPS ping",
                  "Joining these points gives the plane's path, called a trajectory",
                  "Spatio-temporal means we look at WHERE (place) and WHEN (time) together",
                  "Think of it as Google Maps traffic, but for the sky"],
         notes="Every commercial aeroplane has a device called ADS-B that broadcasts its location, height and "
               "speed every second. If we join these points, we get the path of the flight, which is called a "
               "trajectory. Spatio-temporal simply means we study place and time together, for example: how "
               "busy is the sky near Mumbai at 7 pm? You can imagine it like Google Maps showing red roads "
               "for traffic, but here we do it for the sky."),
    dict(kicker="THE PROBLEM", title="Why do we need this?",
         bullets=["Delhi and Mumbai airports are very busy in the morning and evening rush",
                  "When the runway is full, planes circle in the air, called holding",
                  "Planes also fly zig-zag airways instead of straight lines",
                  "Result: extra fuel, more pollution, delays for passengers",
                  "Example: 15 minutes of circling burns roughly 500-600 kg of fuel for an A320"],
         notes="Here is the real problem. Indian airports like Delhi and Mumbai get very crowded at peak hours. "
               "When the runway is busy, air traffic control asks planes to fly in circles and wait. This is "
               "called holding. Also, planes do not always fly straight; they follow fixed air routes that "
               "bend. Both of these waste fuel, add pollution and delay passengers. For example, if an A320 "
               "circles for 15 minutes, it burns around 500 to 600 kilograms of extra fuel. Multiply this by "
               "hundreds of flights every day and the waste is very large."),
    dict(kicker="SDG 9", title="Link to Sustainable Development Goal 9",
         bullets=["SDG 9 = build strong, reliable and sustainable infrastructure",
                  "Airspace and airports are national infrastructure",
                  "Our analysis shows WHERE new capacity is needed",
                  "Shorter routes = less fuel = greener aviation (also helps SDG 13)"],
         notes="SDG 9 asks countries to build infrastructure that is reliable and sustainable. Airports and the "
               "airspace above us are infrastructure, just like roads and railways. Our project gives data to "
               "decide where a new runway or a better route is needed. And when planes fly shorter routes, they "
               "burn less fuel, which also helps climate action, SDG 13."),
    dict(kicker="DATA", title="The dataset",
         bullets=["Source: OpenSky Network, free real flight data used by researchers",
                  "Each row = one plane at one moment: time, plane ID, latitude, longitude, height, speed, direction",
                  "We use 1 real hour of data over India, plus a full 24-hour sample day",
                  "Sample day: 20 airports, 900 flights, about 67,000 position records"],
         notes="Our data comes from the OpenSky Network, a free website used by universities around the world to "
               "study flights. Each row tells us: at this time, this plane was at this latitude and longitude, at "
               "this height, flying at this speed and direction. In our Colab notebook we download one real hour of "
               "data over India. Real data does not tell where a flight started and ended, so we also made a "
               "sample day in the same format for 20 major Indian airports, with 900 flights and about 67,000 "
               "rows. It copies real patterns like the morning and evening rush."),
    dict(kicker="ARCHITECTURE", title="How the system works",
         bullets=["1. Collect: flight position data",
                  "2. Store: Hadoop HDFS, which splits big files across machines",
                  "3. Process: MapReduce and Spark crunch the numbers",
                  "4. Save: MongoDB stores each flight path for map searches",
                  "5. Analyse: graph of airports finds groups and hubs",
                  "6. Show: interactive web dashboard"],
         notes="This is the flow of our system. First we collect the flight data. Then we store it in Hadoop HDFS, "
               "which can split a huge file into blocks and keep them on many computers. Next, MapReduce and "
               "Spark process the data in parallel. We store each flight's path in MongoDB, a NoSQL database "
               "that can search by location. Then we build a network of airports and analyse it. Finally, "
               "everything is shown on a web dashboard."),
    dict(kicker="HADOOP & MAPREDUCE", title="Hadoop and MapReduce",
         bullets=["HDFS commands used: put, ls, cat, cp, mv, get, rm",
                  "Job 1: divide India's map into small boxes and count planes in each box per hour",
                  "Job 2: join each plane's points in time order and measure the distance it really flew",
                  "Compare with the straight-line distance to get the extra % flown",
                  "Like election counting: many booths count at once, then totals are added"],
         notes="In Hadoop we used the basic HDFS commands from our first experiment: put to upload, ls to list, "
               "cat to view, cp and mv to copy and move, get to download, and rm to delete. Then we wrote two "
               "MapReduce jobs. The first one divides the map of India into small boxes and counts how many planes "
               "were in each box every hour. That tells us the crowded areas. The second job collects all points "
               "of one plane, puts them in time order, and calculates how far it actually flew compared to the "
               "straight-line distance. MapReduce works like election counting: many booths count votes at the "
               "same time, which is the map step, and then all counts are added together, which is the reduce step."),
    dict(kicker="SPARK & MONGODB", title="Spark and MongoDB",
         bullets=["Spark reads data straight from HDFS and runs SQL queries fast, in memory",
                  "Finds flight phase: climbing, cruising, descending",
                  "Detects holding: a plane that turned more than 1.5 full circles near an airport",
                  "MongoDB stores each flight path as a map line",
                  "Example search: which flights passed within 50 km of Nagpur?"],
         notes="Spark is faster than MapReduce because it keeps data in memory. We used Spark SQL to count active "
               "planes every hour and to label each point as climbing, cruising or descending. We also detect "
               "holding: if a plane keeps turning in the same direction for more than 540 degrees, that means "
               "one and a half circles, so it is waiting to land. In MongoDB, every flight is saved as a line on "
               "the map with a special geo index. That lets us ask questions like: which flights passed within 50 "
               "kilometres of Nagpur, or which flights entered the Mumbai area during the evening rush."),
    dict(kicker="GRAPH ANALYTICS", title="Airport network: groups and hubs",
         bullets=["Airports = dots, flights between them = lines",
                  "Louvain algorithm finds groups of airports that fly mostly among themselves",
                  "Found 4 regions: North, West, South, East",
                  "PageRank finds the most important hubs: Delhi and Mumbai",
                  "Like finding friend groups and influencers on Instagram"],
         notes="Next we turned the airports into a network. Each airport is a dot and each route is a line. We "
               "used the Louvain community detection algorithm from our syllabus. It found four natural groups: "
               "North, West, South and East India. Then we used PageRank and betweenness to find the most "
               "important airports, which are Delhi and Mumbai. This is exactly like social media analysis: "
               "Louvain finds friend groups, and PageRank finds influencers. Here the influencers are hub airports."),
    dict(kicker="RESULTS", title="What we found",
         bullets=["Flights flew 4.1% more distance than the straight path, on average",
                  "About 17,900 km of extra flying in one day",
                  "About 136 tonnes of CO2 that could be avoided every day",
                  "52 planes had to circle (hold), all at Delhi and Mumbai, at rush hours",
                  "Busiest hours: 6-10 am and 5-9 pm"],
         notes="These are our results for the sample day. On average, flights flew 4.1 percent more than the "
               "straight path. That adds up to nearly 18,000 kilometres of extra flying in one day, which is "
               "about 136 tonnes of carbon dioxide that could be saved. 52 planes had to circle before landing, "
               "all at Delhi and Mumbai, and all during the morning and evening rush. This clearly shows where "
               "and when the infrastructure is under pressure."),
    dict(kicker="LIVE DEMO", title="The dashboard",
         bullets=["Airspace map: every flight path coloured by height, with a time slider",
                  "Heatmap and hotspot boxes show crowded areas",
                  "Temporal tab: traffic by hour, holding by airport",
                  "Route tab: worst routes and CO2 impact",
                  "Network tab: airport groups and hub ranking"],
         notes="Now let me show the dashboard. On the first tab you see every flight path over India. Green is "
               "low, yellow is medium and blue is high altitude. Red paths are planes that circled. I can move "
               "this slider to see flights at any hour. The temporal tab shows the morning and evening peaks. The "
               "route tab lists the routes with the most extra distance and the CO2 impact. The network tab shows "
               "the airport groups found by Louvain and the ranking of hub airports."),
    dict(kicker="USE CASES", title="Who can use this and how",
         bullets=["Airports Authority of India: plan new routes and airspace changes",
                  "Airport operators: decide when a new runway or terminal is needed",
                  "Airlines: choose better routes and departure times to save fuel",
                  "Government: track aviation pollution against climate targets",
                  "Passengers: fewer delays, more on-time flights"],
         notes="Who benefits from this? The Airports Authority of India can use it to plan direct routes and "
               "redesign busy airspace. Airport operators can see when the runway is full and plan new capacity, "
               "like the new Navi Mumbai and Noida airports, which were built because the old ones are crowded. "
               "Airlines can schedule flights away from rush hours and save fuel. The government can track "
               "pollution, and in the end passengers get fewer delays."),
    dict(kicker="CONCLUSION", title="Conclusion and future scope",
         bullets=["Built a complete big data pipeline: Hadoop, MapReduce, Spark, MongoDB, Graphs",
                  "Turned raw flight points into useful decisions for infrastructure",
                  "Future: live data with Kafka, predict delays with machine learning, add weather data",
                  "Thank you!"],
         notes="To conclude, we built a full big data pipeline using the tools from our syllabus and used it to "
               "turn raw flight points into useful insights for infrastructure planning. In future we can connect "
               "live data using Kafka, predict delays using machine learning, and add weather data, because fog "
               "in Delhi is a major cause of delays. Thank you, we are happy to take questions."),
]
