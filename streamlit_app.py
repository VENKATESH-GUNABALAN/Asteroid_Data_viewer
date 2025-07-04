import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date

# MySQL database credentials
MYSQL_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
MYSQL_USER = "4Gu6Uh2tH3NsLam.root"
MYSQL_PASSWORD = "JF4Toi6vzdZzso0d"
MYSQL_PORT = 4000
MYSQL_DATABASE = "Asteroid_Data_1"

# Function to connect to MySQL database
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT,
            database=MYSQL_DATABASE
        )
        if connection.is_connected():
            return connection
        else:
            st.error("Failed to connect to MySQL server")
            return None
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to execute a query and return results as a DataFrame
def execute_query(connection, query, params=None):
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(results)
    except Error as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()

# Predefined SQL queries
QUERIES = {
    "Count asteroid approaches": """
        SELECT a.name, COUNT(c.approach_id) as approach_count
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        GROUP BY a.id, a.name
        ORDER BY approach_count DESC;
    """,
    "Average velocity per asteroid": """
        SELECT a.name, AVG(c.relative_velocity_kmph) as avg_velocity_kmph
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        GROUP BY a.id, a.name
        ORDER BY avg_velocity_kmph DESC;
    """,
    "Top 10 fastest asteroids": """
        SELECT a.name, MAX(c.relative_velocity_kmph) as max_velocity_kmph
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        GROUP BY a.id, a.name
        ORDER BY max_velocity_kmph DESC
        LIMIT 10;
    """,
    "Hazardous asteroids with >3 approaches": """
        SELECT a.name, COUNT(c.approach_id) as approach_count
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE a.is_potentially_hazardous_asteroid = TRUE
        GROUP BY a.id, a.name
        HAVING approach_count > 3
        ORDER BY approach_count DESC;
    """,
    "Month with most approaches": """
        SELECT DATE_FORMAT(c.close_approach_date, '%Y-%m') as month, 
               COUNT(*) as approach_count
        FROM close_approach c
        GROUP BY month
        ORDER BY approach_count DESC
        LIMIT 1;
    """,
    "Asteroid with fastest approach": """
        SELECT a.name, c.relative_velocity_kmph, c.close_approach_date
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        ORDER BY c.relative_velocity_kmph DESC
        LIMIT 1;
    """,
    "Asteroids by max diameter (descending)": """
        SELECT a.name, a.estimated_diameter_max_km
        FROM asteroids a
        ORDER BY a.estimated_diameter_max_km DESC;
    """,
    "Asteroid with decreasing miss distance": """
        SELECT a.name, c.close_approach_date, c.miss_distance_astronomical
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.miss_distance_astronomical IS NOT NULL
        ORDER BY a.id, c.close_approach_date, c.miss_distance_astronomical;
    """,
    "Closest approach per asteroid": """
        SELECT a.name, c.close_approach_date, c.miss_distance_astronomical
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE (a.id, c.miss_distance_astronomical) IN (
            SELECT a2.id, MIN(c2.miss_distance_astronomical)
            FROM asteroids a2
            JOIN close_approach c2 ON a2.id = c2.neo_reference_id
            GROUP BY a2.id
        )
        ORDER BY c.miss_distance_astronomical;
    """,
    "Asteroids with velocity > 50,000 km/h": """
        SELECT a.name, c.relative_velocity_kmph, c.close_approach_date
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.relative_velocity_kmph > 50000
        ORDER BY c.relative_velocity_kmph DESC;
    """,
    "Approaches per month": """
        SELECT DATE_FORMAT(c.close_approach_date, '%Y-%m') as month, 
               COUNT(*) as approach_count
        FROM close_approach c
        GROUP BY month
        ORDER BY month;
    """,
    "Asteroid with highest brightness": """
        SELECT a.name, a.absolute_magnitude_h
        FROM asteroids a
        WHERE a.absolute_magnitude_h = (
            SELECT MIN(absolute_magnitude_h) 
            FROM asteroids
            WHERE absolute_magnitude_h IS NOT NULL
        );
    """,
    "Hazardous vs non-hazardous count": """
        SELECT is_potentially_hazardous_asteroid, 
               COUNT(*) as asteroid_count
        FROM asteroids
        GROUP BY is_potentially_hazardous_asteroid;
    """,
    "Asteroids closer than Moon (<1 LD)": """
        SELECT a.name, c.close_approach_date, c.miss_distance_lunar
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.miss_distance_lunar < 1
        ORDER BY c.miss_distance_lunar;
    """,
    "Asteroids within 0.05 AU": """
        SELECT a.name, c.close_approach_date, c.miss_distance_astronomical
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.miss_distance_astronomical < 0.05
        ORDER BY c.miss_distance_astronomical;
    """,
    "Asteroids with multiple approaches in a year": """
        SELECT a.name, DATE_FORMAT(c.close_approach_date, '%Y') as year, 
               COUNT(*) as approach_count
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        GROUP BY a.id, a.name, year
        HAVING approach_count > 1
        ORDER BY year, approach_count DESC;
    """,
    "Closest approach by hazardous asteroids": """
        SELECT a.name, MIN(c.miss_distance_astronomical) as min_miss_distance_au
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE a.is_potentially_hazardous_asteroid = TRUE
        GROUP BY a.id, a.name
        ORDER BY min_miss_distance_au;
    """,
    "High velocity, small asteroids": """
        SELECT a.name, c.relative_velocity_kmph, a.estimated_diameter_max_km
        FROM SSAsteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.relative_velocity_kmph > 70000 AND a.estimated_diameter_max_km < 0.1
        ORDER BY c.relative_velocity_kmph DESC;
    """,
    "Average miss distance by orbiting body": """
        SELECT c.orbiting_body, AVG(c.miss_distance_lunar) as avg_miss_distance_lunar
        FROM close_approach c
        GROUP BY c.orbiting_body
        ORDER BY avg_miss_distance_lunar;
    """,
    "Largest asteroids with close approaches (<0.1 AU)": """
        SELECT a.name, a.estimated_diameter_max_km, MIN(c.miss_distance_astronomical) as min_miss_distance_au
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.miss_distance_astronomical < 0.1
        GROUP BY a.id, a.name, a.estimated_diameter_max_km
        ORDER BY a.estimated_diameter_max_km DESC
        LIMIT 10;
    """,
    "Asteroids approaching on specific dates": """
        SELECT a.name, c.close_approach_date, c.miss_distance_astronomical
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.close_approach_date IN ('2024-01-01', '2024-06-01', '2024-12-31')
        ORDER BY c.close_approach_date;
    """,
    "Brightness vs hazard correlation": """
        SELECT 
            CASE 
                WHEN a.absolute_magnitude_h < 15 THEN '<15 (Very Bright)'
                WHEN a.absolute_magnitude_h < 20 THEN '15-20 (Bright)'
                WHEN a.absolute_magnitude_h < 25 THEN '20-25 (Moderate)'
                ELSE '>=25 (Faint)'
            END as brightness_bin,
            a.is_potentially_hazardous_asteroid,
            COUNT(*) as asteroid_count
        FROM asteroids a
        GROUP BY brightness_bin, a.is_potentially_hazardous_asteroid
        ORDER BY brightness_bin;
    """
}

# Streamlit app
st.title("Asteroid Data Explorer")

# Sidebar for mode selection
st.sidebar.header("Select Mode")
mode = st.sidebar.radio("Choose an option", ["Predefined Queries", "Filter Asteroid Data"])


# Connect to database
connection = connect_to_mysql()

if connection:
    if mode == "Predefined Queries":
        # Sidebar for predefined queries
        st.sidebar.header("Predefined Queries")
        selected_query = st.sidebar.selectbox("Select a query", list(QUERIES.keys()), key="query_select")
        
        # Display results of selected query
        st.header(f"Results for: {selected_query}")
        df = execute_query(connection, QUERIES[selected_query])
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No results found for this query.")
    
    elif mode == "Filter Asteroid Data":
        # Main page filters
        st.header("Filter Asteroid Data")
        st.write("Select criteria to filter asteroid and close approach data")

        # Filter widgets
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.date_input(
                "Close Approach Date Range",
                [date(2024, 1, 1), date(2024, 12, 31)],
                min_value=date(2000, 1, 1),
                max_value=date(2025, 12, 31),
                key="date_filter"
            )
            velocity_range = st.slider(
                "Relative Velocity (km/h)",
                min_value=0.0,
                max_value=100000.0,
                value=(0.0, 100000.0),
                step=1000.0,
                key="velocity_filter"
            )
            diameter_min = st.slider(
                "Min Estimated Diameter (km)",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.01,
                key="diameter_min_filter"
            )

        with col2:
            au_range = st.slider(
                "Miss Distance (Astronomical Units)",
                min_value=0.0,
                max_value=0.5,
                value=(0.0, 0.5),
                step=0.01,
                key="au_filter"
            )
            lunar_range = st.slider(
                "Miss Distance (Lunar Distances)",
                min_value=0.0,
                max_value=100.0,
                value=(0.0, 100.0),
                step=1.0,
                key="lunar_filter"
            )
            diameter_max = st.slider(
                "Max Estimated Diameter (km)",
                min_value=0.0,
                max_value=2.0,
                value=2.0,
                step=0.01,
                key="diameter_max_filter"
            )

        hazardous = st.selectbox(
            "Hazardous Status",
            ["All", "Hazardous", "Non-Hazardous"],
            key="hazardous_filter"
        )

        # Construct dynamic SQL query based on filters
        base_query = """
        SELECT a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
               a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
               c.close_approach_date, c.relative_velocity_kmph,
               c.miss_distance_astronomical, c.miss_distance_lunar
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE 1=1
        """
        
        params = []
        if len(date_range) == 2:
            base_query += " AND c.close_approach_date BETWEEN %s AND %s"
            params.extend([date_range[0], date_range[1]])
        
        base_query += " AND c.relative_velocity_kmph BETWEEN %s AND %s"
        params.extend([velocity_range[0], velocity_range[1]])
        
        base_query += " AND c.miss_distance_astronomical BETWEEN %s AND %s"
        params.extend([au_range[0], au_range[1]])
        
        base_query += " AND c.miss_distance_lunar BETWEEN %s AND %s"
        params.extend([lunar_range[0], lunar_range[1]])
        
        base_query += " AND a.estimated_diameter_min_km >= %s"
        params.append(diameter_min)
        
        base_query += " AND a.estimated_diameter_max_km <= %s"
        params.append(diameter_max)
        
        if hazardous == "Hazardous":
            base_query += " AND a.is_potentially_hazardous_asteroid = TRUE"
        elif hazardous == "Non-Hazardous":
            base_query += " AND a.is_potentially_hazardous_asteroid = FALSE"
        
        base_query += " ORDER BY c.close_approach_date;"

        # Display filtered results
        st.subheader("Filtered Results")
        filtered_df = execute_query(connection, base_query, params)
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.warning("No results match the filter criteria.")

    # Close connection
    connection.close()
else:
    st.error("Unable to connect to the database. Please check credentials and try again.")
