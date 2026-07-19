const fs = require('fs');
const path = require('path');

const domains = [
  {
    file: 'airplane-sql-casestudy.html',
    title: 'SkyRoute Airlines Analytics',
    subtitle: 'Airplane Domain - SQL Case Study',
    logo: 'AIR',
    accent: '#38bdf8',
    accentLight: '#7dd3fc',
    accentDim: 'rgba(56,189,248,0.13)',
    accentBorder: 'rgba(56,189,248,0.30)',
    accentHover: '#0284c7',
    done: "You've completed the SkyRoute Airlines Analytics Challenge. Smooth landing, analyst.",
    problem: {
      lead: '<strong>SkyRoute Airlines</strong> operates domestic flights across India&apos;s major cities and is gearing up for the <strong>winter holiday travel rush</strong>, the busiest and most profitable quarter of the year.',
      bullets: [
        'Which on-time flights to promote as reliability benchmarks',
        'How revenue is distributed across seat classes',
        'Which passengers deserve priority perks in SkyRoute Rewards',
        'Which flight routes are generating the most revenue'
      ],
      stake: 'The Head of Operations, the Revenue Manager, and the Loyalty Program Director are waiting on your queries before the Q4 planning meeting.'
    },
    tables: [
      { name: 'flights', desc: 'All domestic flights operated by SkyRoute this quarter.', columns: ['flight_id','flight_no','origin','destination','departure_time','arrival_time','status'], rows: [[1,'SK-101','Mumbai','Delhi','06:00','08:10','On-Time'],[2,'SK-202','Delhi','Bangalore','10:30','13:00','Delayed'],[3,'SK-303','Mumbai','Bangalore','14:00','16:15','On-Time'],[4,'SK-404','Bangalore','Chennai','08:45','09:50','Cancelled'],[5,'SK-505','Mumbai','Delhi','19:00','21:05','On-Time']] },
      { name: 'aircraft', desc: 'Aircraft in SkyRoute&apos;s fleet.', columns: ['aircraft_id','model','total_seats','airline'], rows: [[1,'Boeing 737',180,'SkyRoute'],[2,'Airbus A320',165,'SkyRoute'],[3,'Boeing 777',350,'SkyRoute'],[4,'ATR 72',70,'SkyRoute']] },
      { name: 'passengers', desc: 'Registered passengers and frequent flyer tiers.', columns: ['passenger_id','full_name','nationality','frequent_flyer_tier'], rows: [[1,'Meera Joshi','Indian','Gold'],[2,'David Chen','Chinese','Silver'],[3,'Aisha Patel','Indian','Bronze'],[4,'Thomas Wright','British','Gold'],[5,'Neha Saxena','Indian','Silver']] },
      { name: 'bookings', desc: 'Ticket bookings made by passengers across flights.', columns: ['booking_id','passenger_id','flight_id','seat_class','fare','booking_date'], rows: [[1,1,1,'Business',8500,'2024-10-20'],[2,2,2,'Economy',3200,'2024-10-21'],[3,3,1,'Economy',4100,'2024-10-22'],[4,1,3,'First',15000,'2024-10-23'],[5,4,5,'Business',7800,'2024-10-24']] }
    ],
    questions: [
      ['Beginner','The Marketing team is launching a <strong>Fly Punctual with SkyRoute</strong> campaign highlighting on-time flights from Mumbai.','Retrieve the flight number, destination, departure time, and arrival time of all flights departing from Mumbai that have a status of On-Time.'],
      ['Intermediate','The Revenue Manager needs the <strong>Seat Class Revenue Breakdown</strong> for the quarterly review.','For each seat class, find the total number of bookings and the total fare collected.'],
      ['Intermediate','The Loyalty Program Director is reviewing eligibility for <strong>SkyRoute Elite Status</strong> for passengers who booked more than one flight.','Identify passengers who have made more than one booking. Show their name, nationality, frequent flyer tier, and total number of bookings.'],
      ['Advanced','The Revenue team wants a <strong>Route Revenue Leaderboard</strong> showing which flights pull the most fare revenue on each route.','For each flight, show flight number, origin, destination, total fare, route rank, and percentage of route revenue rounded to 2 decimals.']
    ],
    expected: {
      1: [['SK-101','Delhi','06:00','08:10'],['SK-303','Bangalore','14:00','16:15'],['SK-505','Delhi','19:00','21:05']],
      2: [['Business',2,16300],['Economy',2,7300],['First',1,15000]],
      3: [['Meera Joshi','Indian','Gold',2]],
      4: [['SK-202','Delhi','Bangalore',3200,1,100],['SK-303','Mumbai','Bangalore',15000,1,100],['SK-101','Mumbai','Delhi',12600,1,61.76],['SK-505','Mumbai','Delhi',7800,2,38.24]]
    }
  },
  {
    file: 'food-delivery-sql-casestudy.html',
    title: 'QuickBite Analytics',
    subtitle: 'Food Delivery Domain - SQL Case Study',
    logo: 'PIZ',
    accent: '#ef4444',
    accentLight: '#facc15',
    accentDim: 'rgba(239,68,68,0.13)',
    accentBorder: 'rgba(250,204,21,0.32)',
    accentHover: '#dc2626',
    done: "You've completed the QuickBite Analytics Challenge. The pitch deck has its numbers.",
    problem: {
      lead: '<strong>QuickBite</strong> is one of India&apos;s fastest-growing food delivery platforms. After a record-breaking Diwali season, leadership needs the numbers before their <strong>Series B investor pitch</strong>.',
      bullets: ['Which restaurant partners are actually performing','Which cuisines drive revenue and fast delivery','Who QuickBite&apos;s most loyal customers are','Which restaurants dominate each city'],
      stake: 'The VP of Partnerships, Head of Customer Experience, and City Ops Leads are depending on your queries.'
    },
    tables: [
      { name: 'restaurants', desc: 'Partner restaurants listed on QuickBite.', columns: ['restaurant_id','name','cuisine','city','rating'], rows: [[1,'Spice Garden','Indian','Mumbai',4.5],[2,'Dragon Wok','Chinese','Delhi',4.2],[3,'Pizza Palazzo','Italian','Mumbai',3.8],[4,'Biryani Blues','Indian','Bangalore',4.7],[5,'Sushi Street','Japanese','Delhi',4.1]] },
      { name: 'customers', desc: 'Registered QuickBite users and memberships.', columns: ['customer_id','full_name','city','membership'], rows: [[1,'Ankit Sharma','Mumbai','Prime'],[2,'Divya Nair','Delhi','Regular'],[3,'Rohan Mehta','Mumbai','Prime'],[4,'Preethi Rao','Bangalore','Regular'],[5,'Sahil Gupta','Delhi','Prime']] },
      { name: 'orders', desc: 'Every order with delivery outcome.', columns: ['order_id','customer_id','restaurant_id','order_date','status','delivery_time_mins'], rows: [[1001,1,1,'2024-11-01','Delivered',32],[1002,2,2,'2024-11-03','Delivered',45],[1003,3,3,'2024-11-05','Cancelled',null],[1004,1,4,'2024-11-10','Delivered',28],[1005,3,1,'2024-11-12','Delivered',40]] },
      { name: 'order_items', desc: 'Individual dishes within each order.', columns: ['item_id','order_id','dish_name','quantity','price'], rows: [[1,1001,'Butter Chicken',2,320],[2,1001,'Garlic Naan',3,60],[3,1002,'Fried Rice',1,180],[4,1004,'Chicken Biryani',2,280],[5,1005,'Paneer Tikka',1,250]] }
    ],
    questions: [
      ['Beginner','The Mumbai City Ops Lead wants high-performing restaurant partners for <strong>Top Picks in Mumbai</strong>.','Retrieve the name, cuisine, and rating of all restaurants in Mumbai with rating above 4.0, sorted by rating descending.'],
      ['Intermediate','The VP of Partnerships wants to know which cuisines are real revenue drivers and whether delivery speed is healthy.','For each cuisine, calculate total revenue and average delivery time, considering only delivered orders.'],
      ['Intermediate','The Head of Customer Experience is building a <strong>QuickBite Loyalist Program</strong> for exploratory users.','Identify customers who ordered from more than one unique restaurant. Show name, city, membership, and unique restaurant count.'],
      ['Advanced','City Ops Leads need a <strong>City Restaurant Leaderboard</strong> showing restaurant revenue rank and share within each city.','For each restaurant, show name, city, total revenue, city rank, and percentage of city total rounded to 2 decimals.']
    ],
    expected: { 1: [['Spice Garden','Indian',4.5]], 2: [['Chinese',180,45],['Indian',1630,33]], 3: [['Ankit Sharma','Mumbai','Prime',2]], 4: [['Biryani Blues','Bangalore',560,1,100],['Dragon Wok','Delhi',180,1,100],['Spice Garden','Mumbai',1070,1,100]] }
  },
  {
    file: 'movies-sql-casestudy.html',
    title: 'CineStream Content Analytics',
    subtitle: 'Movies Domain - SQL Case Study',
    logo: 'CIN',
    accent: '#e11d48',
    accentLight: '#fb7185',
    accentDim: 'rgba(225,29,72,0.13)',
    accentBorder: 'rgba(225,29,72,0.30)',
    accentHover: '#be123c',
    done: "You've completed the CineStream Content Analytics Challenge. The strategy room is ready.",
    problem: {
      lead: '<strong>CineStream</strong> is a fast-rising global OTT platform preparing for the <strong>Annual Content Strategy Meeting</strong>.',
      bullets: ['Which movies get featured next quarter','Which genres deserve more investment','Which directors merit a Spotlight Series','How movies rank within their genre'],
      stake: 'The Head of Content, Finance Lead, and Regional Marketing Managers are counting on your queries.'
    },
    tables: [
      { name: 'movies', desc: 'Core catalog of movies on the platform.', columns: ['movie_id','title','genre','release_year','language','director_id'], rows: [[1,'The Last Horizon','Sci-Fi',2021,'English',101],[2,'Rang De Sapne','Drama',2022,'Hindi',102],[3,'Neon City','Thriller',2023,'English',103],[4,'Andha Yug','Drama',2021,'Telugu',102],[5,'Starfall','Sci-Fi',2020,'English',101]] },
      { name: 'directors', desc: 'Director profiles.', columns: ['director_id','full_name','country','debut_year'], rows: [[101,'James Calloway','USA',2015],[102,'Arjun Reddy','India',2018],[103,'Sofia Mendes','Brazil',2019],[104,'Lena Fischer','Germany',2021]] },
      { name: 'box_office', desc: 'Budget and worldwide collection in crores.', columns: ['bo_id','movie_id','budget_cr','collection_cr','release_country'], rows: [[1,1,120,310,'USA'],[2,2,45,98,'India'],[3,3,80,65,'Brazil'],[4,4,30,112,'India'],[5,5,95,220,'USA']] },
      { name: 'reviews', desc: 'User ratings and vote counts.', columns: ['review_id','movie_id','platform','rating','total_votes'], rows: [[1,1,'IMDb',8.2,124000],[2,2,'IMDb',7.5,43000],[3,3,'IMDb',6.8,31000],[4,4,'RottenTomatoes',8.9,18000],[5,5,'IMDb',7.1,89000]] }
    ],
    questions: [
      ['Beginner','The Content team is launching <strong>Best of English Cinema Post-2020</strong> for subscribers.','Retrieve the title and release year of all English language movies released after 2020, sorted by most recent first.'],
      ['Intermediate','Finance is building a <strong>Genre Performance Report</strong> across box office and audience ratings.','For each genre, find total box office collection and average user rating.'],
      ['Intermediate','CineStream is planning a <strong>Director Spotlight Series</strong> for directors with more than one movie.','Show eligible directors, number of movies, and total box office collection.'],
      ['Advanced','Regional Marketing Managers need a <strong>Genre Leaderboard</strong> for licensing and ad pitches.','For each movie, show title, genre, collection, genre rank, and percentage of genre total rounded to 2 decimals.']
    ],
    expected: { 1: [['The Last Horizon',2021],['Neon City',2023]], 2: [['Drama',210,8.2],['Sci-Fi',530,7.65],['Thriller',65,6.8]], 3: [['James Calloway',2,530],['Arjun Reddy',2,210]], 4: [['Andha Yug','Drama',112,1,53.33],['Rang De Sapne','Drama',98,2,46.67],['The Last Horizon','Sci-Fi',310,1,58.49],['Starfall','Sci-Fi',220,2,41.51],['Neon City','Thriller',65,1,100]] }
  },
  {
    file: 'clothing-sql-casestudy.html',
    title: 'StyleHub Retail Analytics',
    subtitle: 'Clothing Domain - SQL Case Study',
    logo: 'STY',
    accent: '#ec4899',
    accentLight: '#f9a8d4',
    accentDim: 'rgba(236,72,153,0.13)',
    accentBorder: 'rgba(236,72,153,0.30)',
    accentHover: '#db2777',
    done: "You've completed the StyleHub Retail Analytics Challenge. The strategy call has its answers.",
    problem: {
      lead: '<strong>StyleHub</strong> is a fast-growing D2C fashion brand reviewing performance after the <strong>festive season</strong>.',
      bullets: ['Which products to push in the Winter Sale','Which customers deserve loyalty offers','Which categories drive revenue','How products perform within category'],
      stake: 'The Head of Merchandising, CRM Lead, and Finance Manager are waiting before the strategy call.'
    },
    tables: [
      { name: 'products', desc: 'The complete catalog of StyleHub items.', columns: ['product_id','name','category','brand','price'], rows: [[1,'Classic White Tee','Tops','UrbanEdge',799],[2,'Slim Fit Chinos','Bottoms','UrbanEdge',1999],[3,'Floral Sundress','Dresses','BloomWear',2499],[4,'Leather Jacket','Outerwear','RawHide',5999],[5,'Cargo Shorts','Bottoms','UrbanEdge',1299]] },
      { name: 'customers', desc: 'Registered customers and loyalty tiers.', columns: ['customer_id','full_name','city','membership_tier'], rows: [[1,'Neha Kapoor','Mumbai','Platinum'],[2,'Ravi Shankar','Delhi','Gold'],[3,'Ananya Singh','Bangalore','Silver'],[4,'Kabir Malhotra','Mumbai','Gold'],[5,'Tanya Bose','Kolkata','Platinum']] },
      { name: 'orders', desc: 'Every order placed on the platform.', columns: ['order_id','customer_id','order_date','status'], rows: [[1001,1,'2024-10-05','Delivered'],[1002,2,'2024-10-12','Delivered'],[1003,3,'2024-11-01','Returned'],[1004,1,'2024-11-15','Delivered'],[1005,4,'2024-11-20','Pending']] },
      { name: 'order_items', desc: 'Line items with quantities and discounts.', columns: ['item_id','order_id','product_id','quantity','discount_pct'], rows: [[1,1001,3,2,10],[2,1001,1,1,0],[3,1002,4,1,5],[4,1004,2,1,0],[5,1005,5,3,15]] }
    ],
    questions: [
      ['Beginner','Merchandising is curating the <strong>Winter Sale</strong> lineup and wants premium items priced above Rs 1,500.','Retrieve name, category, and price of all products priced above 1500, sorted by price descending.'],
      ['Intermediate','Finance needs a clean <strong>Category Revenue Report</strong> excluding returned orders.','For each product category, calculate total revenue from delivered orders only.'],
      ['Intermediate','CRM is designing a <strong>Repeat Buyer Reward Program</strong> for customers with more than one order.','Show customer name, city, membership tier, and total orders for repeat buyers.'],
      ['Advanced','Category heads need a <strong>Product Leaderboard</strong> for revenue rank and category share.','For each product, show name, category, revenue, category rank, and percent of category total rounded to 2 decimals.']
    ],
    expected: { 1: [['Leather Jacket','Outerwear',5999],['Floral Sundress','Dresses',2499],['Slim Fit Chinos','Bottoms',1999]], 2: [['Bottoms',1999],['Dresses',4498.2],['Outerwear',5699.05],['Tops',799]], 3: [['Neha Kapoor','Mumbai','Platinum',2]], 4: [['Cargo Shorts','Bottoms',3312.45,1,62.36],['Slim Fit Chinos','Bottoms',1999,2,37.64],['Floral Sundress','Dresses',4498.2,1,100],['Leather Jacket','Outerwear',5699.05,1,100],['Classic White Tee','Tops',799,1,100]] }
  },
  {
    file: 'ecommerce-sql-casestudy.html',
    title: 'CartX Analytics',
    subtitle: 'Ecommerce Domain - SQL Case Study',
    logo: 'CTX',
    accent: '#22c55e',
    accentLight: '#86efac',
    accentDim: 'rgba(34,197,94,0.13)',
    accentBorder: 'rgba(34,197,94,0.30)',
    accentHover: '#16a34a',
    done: "You've completed the CartX Analytics Challenge. The sale team can breathe again.",
    problem: {
      lead: '<strong>CartX</strong> is preparing for the <strong>Year-End Mega Sale</strong> after a massive Diwali order surge.',
      bullets: ['Which products need urgent restocking','Which payment methods generate revenue','Which customers deserve early access','Which products lead each category'],
      stake: 'Inventory, Payments, CRM, and Category teams need your queries before the sale goes live.'
    },
    tables: [
      { name: 'products', desc: 'CartX active product catalog.', columns: ['product_id','name','category','price','stock_quantity'], rows: [[1,'Wireless Earbuds','Electronics',2499,45],[2,'Yoga Mat','Sports',899,8],[3,'Stainless Steel Bottle','Kitchen',599,0],[4,'Gaming Mouse','Electronics',1799,23],[5,'Running Shoes','Sports',3299,5]] },
      { name: 'customers', desc: 'Registered shoppers and account type.', columns: ['customer_id','full_name','city','account_type'], rows: [[1,'Aman Verma','Pune','Prime'],[2,'Shreya Das','Hyderabad','Registered'],[3,'Kartik Nair','Chennai','Prime'],[4,'Pooja Mehta','Delhi','Guest'],[5,'Vikram Singh','Kolkata','Registered']] },
      { name: 'orders', desc: 'Orders with payment method and status.', columns: ['order_id','customer_id','order_date','payment_method','status'], rows: [[2001,1,'2024-11-01','UPI','Delivered'],[2002,2,'2024-11-05','Credit Card','Delivered'],[2003,3,'2024-11-08','UPI','Returned'],[2004,1,'2024-11-15','Net Banking','Delivered'],[2005,4,'2024-11-20','Credit Card','Delivered']] },
      { name: 'order_items', desc: 'Individual products within each order.', columns: ['item_id','order_id','product_id','quantity','discount_pct'], rows: [[1,2001,1,1,10],[2,2001,4,1,5],[3,2002,5,1,0],[4,2004,2,2,15],[5,2005,3,1,0]] }
    ],
    questions: [
      ['Beginner','Inventory has an urgent alert for products with fewer than 10 units before the Mega Sale.','Retrieve name, category, price, and stock quantity for low-stock products, sorted by stock ascending.'],
      ['Intermediate','Payments needs delivered-order revenue by payment method for negotiation leverage.','For each payment method, calculate total revenue from delivered orders only.'],
      ['Intermediate','CRM is setting up an <strong>Early Access Program</strong> for shoppers with more than one order.','Show qualifying customer name, city, account type, and total orders placed.'],
      ['Advanced','Category Heads need a <strong>Category Product Leaderboard</strong> for banners and discount strategy.','For each product, show name, category, revenue, category rank, and percent of category total rounded to 2 decimals.']
    ],
    expected: { 1: [['Stainless Steel Bottle','Kitchen',599,0],['Running Shoes','Sports',3299,5],['Yoga Mat','Sports',899,8]], 2: [['Credit Card',3898],['Net Banking',1528.3],['UPI',3958.15]], 3: [['Aman Verma','Pune','Prime',2]], 4: [['Wireless Earbuds','Electronics',2249.1,1,56.82],['Gaming Mouse','Electronics',1709.05,2,43.18],['Stainless Steel Bottle','Kitchen',599,1,100],['Running Shoes','Sports',3299,1,68.33],['Yoga Mat','Sports',1528.3,2,31.67]] }
  },
  {
    file: 'cricket-sql-casestudy.html',
    title: 'StrikeZone Analytics',
    subtitle: 'Cricket Domain - SQL Case Study',
    logo: 'PCL',
    accent: '#84cc16',
    accentLight: '#bef264',
    accentDim: 'rgba(132,204,22,0.13)',
    accentBorder: 'rgba(132,204,22,0.30)',
    accentHover: '#65a30d',
    done: "You've completed the StrikeZone Analytics Challenge. The auction board has its numbers.",
    problem: {
      lead: '<strong>StrikeZone Analytics</strong> is the official data partner for the <strong>Premier Cricket League</strong>, with the next player auction two weeks away.',
      bullets: ['Which players are dangerous with the bat','Which teams dominate the scoreboard','Which players are proven across matches','Who leads each team&apos;s run scoring'],
      stake: 'Franchise owners and coaches are waiting on your queries before auction planning.'
    },
    tables: [
      { name: 'teams', desc: 'The four PCL franchises.', columns: ['team_id','team_name','city','coach'], rows: [[1,'Mumbai Mavericks','Mumbai','Sanjay Patel'],[2,'Delhi Dynamos','Delhi','Arun Kapoor'],[3,'Bangalore Blazers','Bangalore','Vijay Nair'],[4,'Chennai Champions','Chennai','Ravi Kumar']] },
      { name: 'players', desc: 'Player profiles across franchises.', columns: ['player_id','full_name','team_id','role','nationality'], rows: [[1,'Aryan Singh',1,'Batsman','Indian'],[2,'Jake Miller',1,'All-rounder','Australian'],[3,'Pradeep Rao',2,'Bowler','Indian'],[4,'Carlos Gomez',2,'Batsman','West Indian'],[5,'Rahul Verma',3,'Batsman','Indian']] },
      { name: 'matches', desc: 'Match fixtures and results.', columns: ['match_id','team1_id','team2_id','match_date','venue','winner_team_id'], rows: [[1,1,2,'2024-04-05','Mumbai',1],[2,3,4,'2024-04-07','Bangalore',3],[3,1,3,'2024-04-10','Delhi',1],[4,2,4,'2024-04-12','Chennai',2],[5,1,4,'2024-04-15','Mumbai',4]] },
      { name: 'innings', desc: 'Individual batting and bowling performance.', columns: ['innings_id','match_id','player_id','runs_scored','balls_faced','wickets_taken','overs_bowled'], rows: [[1,1,1,72,48,0,0],[2,1,2,45,32,1,2],[3,2,5,88,54,0,0],[4,3,1,91,62,0,0],[5,3,3,0,0,3,4]] }
    ],
    questions: [
      ['Beginner','Chennai Champions want Indian batsmen to shortlist for auction strategy.','Retrieve full name, team, and role of all Indian players whose role is Batsman.'],
      ['Intermediate','The broadcaster needs <strong>Team Power Rankings</strong> with total runs and overall strike rate.','For each team, find total runs and team strike rate, rounded to 2 decimals.'],
      ['Intermediate','Auction analysts define a proven player as someone with more than two matches this season.','Identify players with more than 2 matches. Show name, team, matches played, and total runs sorted by total runs descending.'],
      ['Advanced','Each owner wants a <strong>Batting Leaderboard</strong> for retention decisions.','For each player, show name, team, total runs, team rank, and percent of team runs rounded to 2 decimals.']
    ],
    expected: { 1: [['Aryan Singh','Mumbai Mavericks','Batsman'],['Rahul Verma','Bangalore Blazers','Batsman']], 2: [['Bangalore Blazers',88,162.96],['Delhi Dynamos',0,null],['Mumbai Mavericks',208,146.48]], 3: [], 4: [['Rahul Verma','Bangalore Blazers',88,1,100],['Pradeep Rao','Delhi Dynamos',0,1,null],['Aryan Singh','Mumbai Mavericks',163,1,78.37],['Jake Miller','Mumbai Mavericks',45,2,21.63]] }
  }
];

function esc(v) {
  if (v === null || v === undefined) return 'NULL';
  return String(v).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

function sqlValue(v) {
  if (v === null || v === undefined) return 'NULL';
  if (typeof v === 'number') return String(v);
  return `'${String(v).replaceAll("'", "''")}'`;
}

function schemaSql(tables) {
  return tables.map(t => {
    const defs = t.columns.map((c, i) => {
      const sample = t.rows.find(r => r[i] !== null && r[i] !== undefined)?.[i];
      const type = typeof sample === 'number' ? 'REAL' : 'TEXT';
      return `${c} ${type}`;
    }).join(', ');
    const rows = t.rows.map(r => `INSERT INTO ${t.name} VALUES (${r.map(sqlValue).join(',')});`).join('\n      ');
    return `CREATE TABLE ${t.name} (${defs});\n      ${rows}`;
  }).join('\n\n      ');
}

function tableMarkup(table, active) {
  const head = table.columns.map(c => `<th>${esc(c)}</th>`).join('');
  const body = table.rows.map(row => `<tr>${row.map(v => `<td>${esc(v)}</td>`).join('')}</tr>`).join('\n            ');
  return `<div class="tab-panel ${active ? 'active' : ''}" id="tab-${table.name}">
        <p class="tab-desc">${table.desc}</p>
        <table class="dtable"><thead><tr>${head}</tr></thead><tbody>
            ${body}
        </tbody></table>
      </div>`;
}

function questionMarkup(q, i) {
  const n = i + 1;
  const badge = i === 0 ? 'badge-b' : i === 3 ? 'badge-a' : 'badge-i';
  return `<div class="qcard" id="qcard-${n}">
        <div class="qcard-head"><span class="qnum">Question ${n}</span><span class="badge ${badge}">${q[0]}</span></div>
        <div class="qbody">
          <div class="ctx-box"><div class="ctx-label">Business Context</div><p>${q[1]}</p></div>
          <div class="task-box"><div class="task-label">Your Task</div><p>${q[2]}</p></div>
          <div class="editor-wrap">
            <div class="editor-bar"><span class="editor-lang">SQL</span><button class="clear-btn" onclick="clearQ(${n})">Clear</button></div>
            <textarea class="sql-editor" id="ed-${n}" placeholder="-- Write your SQL query here..." onkeydown="handleTab(event)"></textarea>
          </div>
          <div class="action-row"><button class="run-btn" onclick="checkQ(${n})">&#9654; Run Check</button><button class="reset-btn" onclick="clearQ(${n})">Reset</button></div>
          <div class="output-area" id="out-${n}"><div class="output-label">Your Output</div><div class="result-wrap" id="res-${n}"></div><div id="fb-${n}"></div></div>
        </div>
        <div class="solved-banner" id="sb-${n}">OK - Question ${n} solved!</div>
      </div>`;
}

function html(d) {
  const tabs = d.tables.map((t, i) => `<button class="tab-btn ${i === 0 ? 'active' : ''}" onclick="switchTab('${t.name}',this)">${t.name}</button>`).join('\n        ');
  const panels = d.tables.map((t, i) => tableMarkup(t, i === 0)).join('\n\n      ');
  const questions = d.questions.map(questionMarkup).join('\n\n      ');
  const bullets = d.problem.bullets.map(b => `<li>${b}</li>`).join('');
  const pillCount = d.questions.map((_, i) => `<div class="pill" id="p${i + 1}"></div>`).join('');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${d.title} - SQL Case Study</title>
<script src="https://cdn.jsdelivr.net/npm/sql.js@1.10.2/dist/sql-wasm.js"></script>
<style>
:root {
  --bg: #0d1117; --surface: #161b22; --surface2: #21262d; --border: #30363d;
  --accent: ${d.accent}; --accent-light: ${d.accentLight}; --accent-dim: ${d.accentDim}; --accent-border: ${d.accentBorder}; --accent-hover: ${d.accentHover};
  --green: #238636; --green-text: #3fb950; --green-bg: #0d2618;
  --red: #da3633; --red-text: #f85149; --red-bg: #210d0d;
  --yellow: #9e6a03; --yellow-text: #d29922; --yellow-bg: #1f1700;
  --text: #c9d1d9; --text-dim: #8b949e; --text-bright: #f0f6fc;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }
#loader { position: fixed; inset: 0; background: var(--bg); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; gap: 16px; }
.spinner { width: 38px; height: 38px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
#loader p { color: var(--text-dim); font-size: 14px; }
header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 14px 32px; position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.header-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.header-logo { width: 36px; height: 36px; background: var(--accent); color: #08111f; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900; letter-spacing: 0; flex: 0 0 auto; }
header h1 { font-size: 15px; font-weight: 700; color: var(--text-bright); }
header p { font-size: 12px; color: var(--text-dim); }
.progress-wrap { display: flex; align-items: center; gap: 10px; }
.pills { display: flex; gap: 6px; }
.pill { width: 30px; height: 7px; background: var(--border); border-radius: 4px; transition: background .4s; }
.pill.done { background: var(--accent); }
.prog-text { font-size: 12px; color: var(--text-dim); white-space: nowrap; }
main { max-width: 940px; margin: 0 auto; padding: 32px 20px; display: flex; flex-direction: column; gap: 36px; }
.section-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--accent-light); margin-bottom: 12px; }
.card, .qcard { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
.card-body { padding: 24px; }
.prob-text { font-size: 14px; line-height: 1.8; }
.prob-text strong { color: var(--text-bright); }
.prob-bullets { margin: 14px 0 14px 20px; display: flex; flex-direction: column; gap: 5px; font-size: 14px; }
.stake { border-left: 3px solid var(--accent); padding-left: 14px; margin-top: 14px; font-style: italic; color: var(--text-dim); font-size: 13px; }
.table-tabs { display: flex; border-bottom: 1px solid var(--border); padding: 0 20px; overflow-x: auto; }
.tab-btn { background: none; border: none; color: var(--text-dim); padding: 11px 15px; cursor: pointer; font-size: 13px; font-weight: 500; font-family: 'Courier New', monospace; border-bottom: 2px solid transparent; white-space: nowrap; }
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--accent-light); border-bottom-color: var(--accent); }
.tab-panel { display: none; padding: 20px; overflow-x: auto; }
.tab-panel.active { display: block; }
.tab-desc { font-size: 13px; color: var(--text-dim); margin-bottom: 14px; }
.dtable { width: 100%; border-collapse: collapse; font-size: 13px; }
.dtable th { background: var(--surface2); color: var(--accent-light); font-weight: 600; padding: 9px 13px; text-align: left; border: 1px solid var(--border); font-family: 'Courier New', monospace; }
.dtable td { padding: 8px 13px; border: 1px solid var(--border); color: var(--text); }
.dtable tr:nth-child(even) td { background: rgba(255,255,255,.02); }
.qcard { transition: border-color .3s; }
.qcard.solved { border-color: var(--green); }
.qcard-head { padding: 15px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.qnum { font-size: 15px; font-weight: 700; color: var(--text-bright); }
.badge { font-size: 11px; font-weight: 700; padding: 3px 11px; border-radius: 20px; text-transform: uppercase; letter-spacing: .05em; }
.badge-b { background: #0d2618; color: #3fb950; border: 1px solid #238636; }
.badge-i { background: #1f1700; color: #d29922; border: 1px solid #9e6a03; }
.badge-a { background: #210d0d; color: #f85149; border: 1px solid #da3633; }
.qbody { padding: 22px; display: flex; flex-direction: column; gap: 18px; }
.ctx-box { background: var(--accent-dim); border: 1px solid var(--accent-border); border-radius: 8px; padding: 15px; }
.ctx-label, .task-label, .output-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 7px; }
.ctx-label { color: var(--accent-light); }
.ctx-box p, .task-box p { font-size: 14px; line-height: 1.75; }
.ctx-box strong { color: var(--text-bright); }
.task-box { background: var(--surface2); border-radius: 8px; padding: 15px; }
.task-label, .output-label { color: var(--text-dim); }
.task-box p { color: var(--text-bright); }
.editor-wrap { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; transition: border-color .2s; }
.editor-wrap:focus-within { border-color: var(--accent); }
.editor-bar { background: var(--surface2); padding: 7px 13px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
.editor-lang { font-size: 11px; color: var(--text-dim); font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
.clear-btn { background: none; border: none; color: var(--text-dim); font-size: 12px; cursor: pointer; padding: 2px 8px; border-radius: 4px; }
.clear-btn:hover { background: var(--border); color: var(--text); }
.sql-editor { width: 100%; background: #080b10; color: #7ee787; font-family: 'Courier New', Consolas, monospace; font-size: 14px; line-height: 1.65; padding: 16px; border: none; outline: none; resize: vertical; min-height: 110px; tab-size: 4; }
.sql-editor::placeholder { color: #2d3748; }
.action-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.run-btn { background: var(--accent); color: #08111f; border: none; padding: 9px 22px; border-radius: 8px; font-size: 14px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.run-btn:hover:not(:disabled) { background: var(--accent-hover); transform: translateY(-1px); color: #fff; }
.reset-btn { background: none; border: 1px solid var(--border); color: var(--text-dim); padding: 9px 18px; border-radius: 8px; font-size: 13px; cursor: pointer; }
.reset-btn:hover { border-color: var(--text-dim); color: var(--text); }
.output-area { display: none; flex-direction: column; gap: 12px; }
.output-area.show { display: flex; }
.result-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }
.empty-result { padding: 12px 16px; color: var(--text-dim); font-size: 13px; font-style: italic; }
.fb-box { border-radius: 8px; padding: 14px 16px; font-size: 14px; line-height: 1.7; display: flex; gap: 12px; align-items: flex-start; }
.fb-icon { font-size: 14px; flex-shrink: 0; margin-top: 1px; font-weight: 900; }
.fb-content { flex: 1; }
.fb-title { font-weight: 700; margin-bottom: 3px; }
.fb-box.success { background: var(--green-bg); border: 1px solid var(--green); color: var(--green-text); }
.fb-box.error { background: var(--red-bg); border: 1px solid var(--red); color: var(--red-text); }
.fb-box.hint { background: var(--yellow-bg); border: 1px solid var(--yellow); color: var(--yellow-text); }
.fb-box code { font-family: 'Courier New', monospace; font-size: 12px; background: rgba(0,0,0,.3); padding: 2px 6px; border-radius: 4px; display: inline-block; margin-top: 6px; word-break: break-all; }
.solved-banner { display: none; align-items: center; gap: 8px; background: var(--green-bg); border-top: 1px solid var(--green); padding: 11px 22px; font-size: 13px; color: var(--green-text); font-weight: 700; }
.solved-banner.show { display: flex; }
#all-done { display: none; text-align: center; padding: 40px 20px; background: var(--surface); border: 1px solid var(--green); border-radius: 12px; }
#all-done h2 { color: var(--green-text); font-size: 22px; margin-bottom: 8px; }
#all-done p { color: var(--text-dim); font-size: 14px; }
#all-done.show { display: block; }
@media (max-width: 700px) {
  header { padding: 12px 16px; align-items: flex-start; flex-direction: column; }
  main { padding: 24px 14px; }
  .progress-wrap { width: 100%; justify-content: space-between; }
  .pill { width: 24px; }
}
</style>
</head>
<body>
<div id="loader"><div class="spinner"></div><p>Initializing SQL Engine...</p></div>
<header>
  <div class="header-left"><div class="header-logo">${d.logo}</div><div><h1>${d.title} Challenge</h1><p>${d.subtitle}</p></div></div>
  <div class="progress-wrap"><div class="pills">${pillCount}</div><span class="prog-text" id="prog-text">0 / 4 solved</span></div>
</header>
<main>
  <section>
    <p class="section-label">Problem Statement</p>
    <div class="card"><div class="card-body"><div class="prob-text">
      <p>${d.problem.lead}</p><p style="margin-top:12px">Your findings will directly influence decisions on:</p>
      <ul class="prob-bullets">${bullets}</ul><p class="stake">${d.problem.stake}</p>
    </div></div></div>
  </section>
  <section>
    <p class="section-label">Database Tables</p>
    <div class="card"><div class="table-tabs">
        ${tabs}
      </div>
      ${panels}
    </div>
  </section>
  <section>
    <p class="section-label">Questions</p>
    <div style="display:flex;flex-direction:column;gap:22px">
      ${questions}
    </div>
  </section>
  <div id="all-done"><h2>All Questions Solved!</h2><p>${d.done}</p></div>
</main>
<script>
let db = null;
const solved = { 1: false, 2: false, 3: false, 4: false };
const EXP = ${JSON.stringify(d.expected)};
const HINTS = {
  generic: {
    noRows: "Your query returned no rows. Check the joins and filters against the sample data.",
    wrongCount: "The row count is different from the expected answer. Recheck the filters, grouping, or HAVING clause.",
    wrongValues: "The row count is close, but one or more values do not match. Review selected columns, calculations, and rounding."
  }
};
initSqlJs({ locateFile: f => 'https://cdn.jsdelivr.net/npm/sql.js@1.10.2/dist/' + f })
  .then(SQL => {
    db = new SQL.Database();
    db.run(\`
      ${schemaSql(d.tables)}
    \`);
    document.getElementById('loader').style.display = 'none';
  })
  .catch(e => {
    document.getElementById('loader').innerHTML = '<p style="color:var(--red-text)">Failed to load SQL engine: ' + e.message + '</p>';
  });
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}
function handleTab(e) {
  if (e.key !== 'Tab') return;
  e.preventDefault();
  const t = e.target, s = t.selectionStart;
  t.value = t.value.slice(0, s) + '    ' + t.value.slice(t.selectionEnd);
  t.selectionStart = t.selectionEnd = s + 4;
}
function clearQ(n) {
  document.getElementById('ed-' + n).value = '';
  document.getElementById('out-' + n).classList.remove('show');
}
function renderTable(result) {
  if (!result || !result.length) return '<p class="empty-result">Query returned 0 rows.</p>';
  const columns = result[0].columns, values = result[0].values;
  let h = '<table class="dtable"><thead><tr>';
  columns.forEach(c => h += '<th>' + c + '</th>');
  h += '</tr></thead><tbody>';
  values.forEach(row => {
    h += '<tr>';
    row.forEach(v => h += '<td>' + (v ?? 'NULL') + '</td>');
    h += '</tr>';
  });
  return h + '</tbody></table>';
}
function norm(v) {
  if (v === null || v === undefined) return '';
  const n = parseFloat(v);
  return isNaN(n) ? String(v).toLowerCase().trim() : Math.round(n * 100) / 100;
}
function sortRows(rows) {
  return [...rows].sort((a, b) => {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const av = String(a[i] ?? ''), bv = String(b[i] ?? '');
      if (av < bv) return -1;
      if (av > bv) return 1;
    }
    return 0;
  });
}
function matches(actualValues, expected) {
  if (actualValues.length !== expected.length) return false;
  const as = sortRows(actualValues.map(r => r.map(norm)));
  const es = sortRows(expected.map(r => r.map(norm)));
  for (let i = 0; i < as.length; i++) {
    if (as[i].length !== es[i].length) return false;
    for (let j = 0; j < as[i].length; j++) {
      const a = as[i][j], e = es[i][j];
      if (typeof a === 'number' && typeof e === 'number') {
        if (Math.abs(a - e) > 0.1) return false;
      } else if (a !== e) return false;
    }
  }
  return true;
}
function showFb(n, type, title, body) {
  const icon = type === 'success' ? 'OK' : type === 'error' ? 'X' : '!';
  document.getElementById('fb-' + n).innerHTML = '<div class="fb-box ' + type + '"><span class="fb-icon">' + icon + '</span><div class="fb-content"><div class="fb-title">' + title + '</div>' + (body ? '<div>' + body + '</div>' : '') + '</div></div>';
}
function markSolved(n) {
  if (solved[n]) return;
  solved[n] = true;
  document.getElementById('qcard-' + n).classList.add('solved');
  document.getElementById('sb-' + n).classList.add('show');
  document.getElementById('p' + n).classList.add('done');
  const count = Object.values(solved).filter(Boolean).length;
  document.getElementById('prog-text').textContent = count + ' / 4 solved';
  if (count === 4) document.getElementById('all-done').classList.add('show');
}
function getHint(n, result) {
  const rows = result && result.length ? result[0].values : [];
  const expected = EXP[n];
  if (matches(rows, expected)) return ['success', 'Correct!', 'Your output matches the expected result. Question ' + n + ' solved!'];
  if (rows.length === 0) return ['hint', 'No Results', HINTS.generic.noRows];
  if (rows.length !== expected.length) return ['hint', 'Row Count Mismatch', HINTS.generic.wrongCount];
  return ['hint', 'Close, but Not Quite', HINTS.generic.wrongValues];
}
function checkQ(n) {
  if (!db) { alert('SQL engine still loading - please wait a moment.'); return; }
  const query = document.getElementById('ed-' + n).value.trim();
  if (!query) { alert('Please write a query first.'); return; }
  const outEl = document.getElementById('out-' + n);
  outEl.classList.add('show');
  document.getElementById('res-' + n).innerHTML = '';
  document.getElementById('fb-' + n).innerHTML = '';
  let result;
  try {
    result = db.exec(query);
  } catch (err) {
    showFb(n, 'error', 'SQL Error', '<code>' + err.message + '</code>');
    return;
  }
  document.getElementById('res-' + n).innerHTML = renderTable(result);
  const fb = getHint(n, result);
  showFb(n, fb[0], fb[1], fb[2]);
  if (fb[0] === 'success') markSolved(n);
}
</script>
</body>
</html>
`;
}

for (const domain of domains) {
  fs.writeFileSync(path.join(__dirname, domain.file), html(domain), 'utf8');
  console.log(`wrote ${domain.file}`);
}
