## 🚌 **AI Smart College Bus – ETA Prediction System**



#### 📌 Project Overview

The AI Smart College Bus is a machine-learning-based prototype designed to estimate the time a college bus may take to reach a selected stop. It provides a simple interface where students can select a bus and destination stop, view the remaining route distance, and obtain an estimated travel time.



#### 🎯 Objectives

\- Predict estimated bus travel time using machine learning.

\- Provide a simple interface for students to check an arrival estimate.

\- Demonstrate route progress and remaining distance.

\- Explore how traffic conditions, speed, time of day, and distance can affect travel time.



#### ✨ Features

\- Student demo login.

\- Bus and destination-stop selection.

\- Automatic remaining-distance calculation using sample route data.

\- Adjustable simulated bus position, speed, time, and traffic.

\- ETA prediction using a trained Random Forest regression model.

\- Visual route progress: Start, 25%, 50%, 75%, and Destination.

\- Streamlit web interface.



#### 🛠️ Technologies Used

\- Python

\- Pandas

\- Machine Learning: Random Forest Regression

\- Streamlit

\- Pickle for saving and loading the trained model



#### ⚙️ How It Works

1\. The student enters a demo name and ID.

2\. The student selects a demo bus and destination stop.

3\. The application calculates the remaining distance from the sample route.

4\. The student adjusts the simulated bus position and other input values.

5\. The trained model predicts an estimated travel time.

6\. The interface displays the ETA and illustrative route progress.



#### 📊 Dataset and Model

The current prototype uses simulated bus-trip data. The model predicts travel time based on input features such as distance, average speed, time of day, traffic condition, and stops remaining.



The model's reported Mean Absolute Error (MAE) during an earlier test run was approximately 1.68 minutes. This result is from simulated data and should not be interpreted as proven accuracy for real buses.



#### ⚠️ Limitations

\- The dataset contains simulated rather than verified real-world bus trips.

\- Bus position is manually simulated; live GPS tracking is not implemented.

\- Live traffic and real map-based road distances are not integrated.

\- The login is for demonstration only and is not secure authentication.

\- The application is a local prototype, not a production deployment.



#### 🚀 Future Improvements

\- Train and evaluate the model on real bus-trip data.

\- Integrate GPS tracking and live location updates.

\- Obtain road distances from a mapping or routing service.

\- Add secure student authentication.

\- Deploy the application online.

\- Monitor prediction performance using real-world trips.

##### 

##### ▶️ Run Locally

1\. Install Python and the required libraries.

2\. Open a terminal in the project folder.

3\. Install the dependencies used by the application, for example:



&#x20;  `pip install streamlit pandas scikit-learn`



4\. Ensure the trained model file `bus\_eta\_model.pkl` and the application file `demo\_app.py` are in the same folder.

5\. Start the application:



&#x20;  `streamlit run demo\_app.py`



##### 👨‍🎓 Project Status

Working educational prototype demonstrating machine-learning-based ETA prediction with simulated routes and bus conditions.

