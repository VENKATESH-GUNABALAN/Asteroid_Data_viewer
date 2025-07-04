# NASA Near-Earth Objects (NEO) Tracking and Insights Using Public API

## System Architecture

1. **Fetch NEO Data**  
   Fetches asteroid data from NASA's public API endpoint and saves it to a JSON file (`neo_data_complete.json`).

2. **Process NEO Data**  
   Reads the fetched JSON file, creates two lists (`asteroid_data` and `close_approach_data`), iterates through the JSON, validates the data, and appends rows to the lists. Returns the two lists: `asteroid_data` and `close_approach_data`.

3. **Connect to MySQL**  
   Establishes a connection to a MySQL database (`Asteroid_Data_5`) using provided credentials. Creates two tables (`asteroids` and `close_approach`) with appropriate schemas if they do not already exist. Returns the connection and cursor objects.

4. **Insert NEO Data**  
   Takes the connection, cursor objects, and the two lists (`asteroid_data` and `close_approach_data`). Constructs SQL queries to insert the list elements into the respective tables according to their schemas. Uses the connection and cursor objects to insert data into the MySQL tables.

5. **Streamlit Visualization**  
   Connects to the MySQL database, fetches data using predefined SQL queries, and converts the results into Pandas DataFrames. Constructs composite queries based on Streamlit input objects (e.g., sliders) and a base SQL query, fetches the filtered data, and converts it into a Pandas DataFrame. Displays the visualization results in a web browser.

## Steps to Run

1. **Google Colab**  
   Execute the cell containing the `main` function.

2. **Streamlit**  
   Run the Streamlit application using the command:  
   ```bash
   streamlit run streamlit_app.py
   ```