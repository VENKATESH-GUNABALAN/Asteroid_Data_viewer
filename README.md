NASA NEAR-EARTH-OBJECTS (NEO) TRACKING AND INSIGHTS USING PUBLIC API

System architecture:
	
	1.Fetch _neo_data : Fetches asteroid data from NASA website using public api endpoint -- saves the downloaded data in a json file (neo_data_complete.json).
    2.Process_neo_data : Reads the fetched json file -- creates two lists (asteroid_data, close_approach_data) -- iterates the json and appends rows into the created lists, after data validation -- returns two lists (asteroid_data, close_approach_data).
    3. Connect_to_mysql : Creates connection to mysql DB (Asteroid_Data_5) using the credentials, creates two tables (asteroids, close approach) -- with appropriate rows, if not already exists in the DB  and returns connection, cursor objects.
    4. Insert_neo_data : Takes connection, cursor objects along with two lists asteroid_data, close_approach_data -- creates sql queries to insert the list elements into appropriate tables as per the respective table schemas -- connects to the sql server using connection object and inserts data into the two sql tables using the cursor objects.
    5. Streamlit : Creates connection the sql DB, using predefined sql queries and cursor object fetches the table and converts it into pandas dataframe(for predefined queries) -- using streamlit input objects (sliders) and a sql base_query, a composite query is constructed and using cursor object fetches the table and converts it into pandas dataframe(for filter queries) -- displays the visualization result in a web browser.

Steps to run : 
    1. Colab - run the cell containing main function
    2. streamlit run streamlit_app.py
    