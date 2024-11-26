import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Set up page configuration
st.set_page_config(page_title="Conference Room Booking", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .title {
            text-align: center;
            color: #003366;
        }
        .booking-table th {
            background-color: #4CAF50;
            color: white;
            padding: 8px;
        }
        .booking-table td {
            padding: 8px;
            text-align: left;
        }
        .low-priority {
            background-color: #e0f7fa;
        }
        .medium-low-priority {
            background-color: #80deea;
        }
        .medium-priority {
            background-color: #ffcc80;
        }
        .medium-high-priority {
            background-color: #ff7043;
        }
        .high-priority {
            background-color: #e57373;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page:", ["View Bookings","Book a Conference Room","Admin"])

# Load the bookings from CSV
BOOKINGS1_FILE = "conference_bookings.csv"

if os.path.exists(BOOKINGS1_FILE):
    bookings_df = pd.read_csv(BOOKINGS1_FILE)
    try:
        bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce").dt.date
        bookings_df["Start"] = pd.to_datetime(bookings_df["Start"], errors="coerce")
        bookings_df["End"] = pd.to_datetime(bookings_df["End"], errors="coerce")
        bookings_df = bookings_df.dropna(subset=["Date", "Start", "End"])
    except Exception as e:
        st.error(f"Error processing the bookings file: {e}")
        bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])
else:
    bookings_df = pd.DataFrame(columns=["User", "Email", "Date", "Room", "Priority", "Description", "Start", "End"])

# Save bookings to the CSV file
def save_bookings(df):
    df.to_csv(BOOKINGS1_FILE, index=False)

# Email-sending function
def send_email(user_email, user_name, room, date, start_time, end_time):
    sender_email = "fahmad@phoenixteam.com"
    sender_password = "qbtmrkwyspwxpbln"
    smtp_server = "smtp-mail.outlook.com"
    smtp_encryption = "STARTTLS"
    smtp_port = 587

    subject = "Conference Room Booking Confirmation"
    body = f"""
    <html>
        <body>
            <p>Dear {user_name},</p>
            <p>Your booking has been confirmed! Here are the details:</p>
            <table border="1" style="border-collapse: collapse; width: 50%; text-align: left;">
                <tr>
                    <th style="padding: 8px; background-color: #f2f2f2;">Field</th>
                    <th style="padding: 8px; background-color: #f2f2f2;">Details</th>
                </tr>
                <tr>
                    <td style="padding: 8px;">Room</td>
                    <td style="padding: 8px;">{room}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Date</td>
                    <td style="padding: 8px;">{date.strftime('%A, %B %d, %Y')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Time</td>
                    <td style="padding: 8px;">{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</td>
                </tr>
            </table>
            <p>If you have any questions, feel free to contact us.</p>
            <p>Best regards,<br>Conference Room Booking Team</p>
        </body>
    </html>
    """
    
    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = f"{user_email}, kteja@phoenixteam.com"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"Email confirmation sent to {user_email} and admin.")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to validate email format using regex
# Function to validate email format using regex and domain check
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@phoenixteam\.com$'
    return re.match(email_regex, email) is not None
# Function to check if the time slot overlaps with any existing bookings
def is_time_slot_available(bookings_df, room, selected_date, start_datetime, end_datetime):
    conflicts = bookings_df[(bookings_df["Date"] == pd.Timestamp(selected_date)) & (bookings_df["Room"] == room)]
    for _, booking in conflicts.iterrows():
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Booking Form Section
# Function to check if the time slot overlaps with any existing bookings
def is_time_slot_available(bookings_df, room, selected_date, start_datetime, end_datetime):
    # Filter bookings that match the room and date
    conflicts = bookings_df[(bookings_df["Date"] == selected_date) & (bookings_df["Room"] == room)]
    
    # Check if the new booking overlaps with any existing booking
    for _, booking in conflicts.iterrows():
        # Check if the new booking overlaps with an existing booking
        if (start_datetime < booking["End"]) and (end_datetime > booking["Start"]):
            return False
    return True

# Function to save the bookings to the CSV file
def save_bookings(df):
    df.to_csv("conference_bookings.csv", index=False)

# Booking Form Section
if page == "Book a Conference Room":
    st.image("https://phoenixteam.com/wp-content/uploads/2024/02/Phoenix-Logo.png", width=200)
    st.write('<h1 class="title">Book a Conference Room</h1>', unsafe_allow_html=True)
    
    with st.form("booking_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            user_name = st.text_input("Your Name", placeholder="Enter your full name")
            user_email = st.text_input("Your Email", placeholder="Enter your email")
        with col2:
            selected_room = st.selectbox("Choose Room", ["Collaborate", "Innovate", "Echo", "Vibe"])
        with col3:
            priority = st.selectbox("Priority Level", ["Low", "Medium-Low", "Medium", "Medium-High", "High"])

        description = st.text_area("Booking Description (optional)", placeholder="Enter details of your booking")
        selected_date = st.date_input("Select Date", min_value=datetime.today().date())
        
        start_time = st.time_input("Start Time", value=time(11, 0))
        end_time = st.time_input("End Time", value=time(12, 0))

        # Define allowed booking time range
        min_time = time(11, 0)  # 11:00 AM
        max_time = time(20, 0)  # 8:00 PM

        # Prevent zero-duration bookings
        if start_time >= end_time:
            st.error("⚠️ End time must be later than start time.")
            valid_times = False
        elif start_time < min_time or end_time > max_time:
            st.error(f"⚠️ Booking times must be between {min_time.strftime('%H:%M')} and {max_time.strftime('%H:%M')}.")
            valid_times = False
        else:
            start_datetime = datetime.combine(selected_date, start_time)
            end_datetime = datetime.combine(selected_date, end_time)
            valid_times = True

        # Validation checks
        valid_name = valid_email = conflict = False

        if not user_name:
            st.error("⚠️ Name cannot be empty.")
            valid_name = False
        else:
            valid_name = True

        if not user_email:
            st.error("⚠️ Email cannot be empty.")
            valid_email = False
        elif not is_valid_email(user_email):
            st.error("⚠️ Please enter a valid email address.")
            valid_email = False
        else:
            valid_email = True

        # Check if the time slot is available
        if valid_times and not is_time_slot_available(bookings_df, selected_room, selected_date, start_datetime, end_datetime):
            st.error("⚠️ The selected time slot is already booked for this room.")
            conflict = True
            valid_times = False

        submit_button = st.form_submit_button("Book Room")

        if submit_button and valid_name and valid_email and valid_times and not conflict:
            # Proceed with booking if valid
            new_booking = {
                "User": user_name,
                "Email": user_email,
                "Date": selected_date,
                "Room": selected_room,
                "Priority": priority,
                "Description": description,
                "Start": start_datetime,
                "End": end_datetime,
            }

            # Add new booking to the DataFrame
            new_booking_df = pd.DataFrame([new_booking])
            bookings_df = pd.concat([bookings_df, new_booking_df], ignore_index=True)

            # Save the updated bookings DataFrame
            save_bookings(bookings_df)

            st.success(f"🎉 Your room has been successfully booked! A confirmation email has been sent to {user_email}.")
            send_email(user_email, user_name, selected_room, selected_date, start_datetime, end_datetime)
        elif submit_button:
            st.error("⚠️ Please ensure all fields are valid and try again.")
# Admin Page: View all bookings with a Calendar
# View Bookings Page
if page == "View Bookings":
    st.write("### Conference Booking📆")
    st.image("https://backdocket.com/wp-content/uploads/2020/01/About-icon.gif")
    st.write("### View Bookings by Date")
    
    # Ensure the Date column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(bookings_df["Date"]):
        bookings_df["Date"] = pd.to_datetime(bookings_df["Date"], errors="coerce")
    
    # Add a calendar widget for selecting the date
    selected_view_date = st.date_input(
        "Select a date to view bookings",
        value=datetime.today().date(),  # Default to today's date
        min_value=None,                # Allow past dates
        max_value=None                 # No restriction on future dates
    )
    
    # Filter the bookings DataFrame for the selected date
    filtered_bookings = bookings_df[
        bookings_df["Date"].dt.date == selected_view_date
    ]
    
    if not filtered_bookings.empty:
        # Convert datetime objects to readable strings for display
        filtered_bookings["Date"] = filtered_bookings["Date"].apply(lambda x: x.strftime('%A, %B %d, %Y'))
        filtered_bookings["Start"] = filtered_bookings["Start"].dt.strftime('%H:%M')
        filtered_bookings["End"] = filtered_bookings["End"].dt.strftime('%H:%M')

        # Priority color mapping
        def get_priority_color(priority):
            priority_colors = {
                "Low": "background-color: #98FB98",  # Light green
                "Medium-Low": "background-color: #FFFF99",  # Light yellow
                "Medium": "background-color: #FFCC66",  # Light orange
                "Medium-High": "background-color: #FF9966",  # Darker orange
                "High": "background-color: #FF6666",  # Light red
            }
            return priority_colors.get(priority, "")

        def style_priority(val):
            return get_priority_color(val)

        # Apply color coding to the priority column
        styled_df = filtered_bookings.style.applymap(style_priority, subset=["Priority"])
        
        # Display the styled DataFrame
        st.dataframe(styled_df)
    else:
        st.write(f"No bookings found for {selected_view_date.strftime('%A, %B %d, %Y')}.")

# Admin Page: Admin Login for booking management
# Admin Page: Admin Login for booking management
if page == "Admin":
    # Admin Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.write("### Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")
    else:
        st.write("### Admin Dashboard")
        st.write("#### Manage Bookings")
        
        if not bookings_df.empty:
            # Display all bookings in a table
            st.write("### All Current Bookings")
            st.dataframe(bookings_df[["User", "Email", "Room", "Date", "Start", "End", "Priority", "Description"]])
            
            # Delete Booking
            booking_to_delete = st.selectbox("Select Booking to Delete", bookings_df["User"].unique())
            if st.button("Delete Booking"):
                bookings_df = bookings_df[bookings_df["User"] != booking_to_delete]
                save_bookings(bookings_df)
                st.success(f"Booking by {booking_to_delete} has been deleted.")

                # Check for time conflicts
                conflict = False
                for _, booking in bookings_df[(bookings_df["Date"] == pd.Timestamp(updated_date)) & (bookings_df["Room"] == updated_room)].iterrows():
                    if (updated_start_datetime < booking["End"]) and (updated_end_datetime > booking["Start"]) and booking["User"] != booking_to_update:
                        conflict = True
                        st.error("⚠️ This time slot is already booked! Please choose a different time.")
                        break
                
                if st.form_submit_button("Update Booking") and not conflict:
                    # Update the booking in the DataFrame
                    bookings_df.loc[bookings_df["User"] == booking_to_update, ["User", "Email", "Room", "Priority", "Description", "Date", "Start", "End"]] = [
                        updated_user_name, updated_user_email, updated_room, updated_priority, updated_description, updated_date, updated_start_datetime, updated_end_datetime
                    ]
                    save_bookings(bookings_df)

                    # Send updated email confirmation
                    send_email(updated_user_email, updated_user_name, updated_room, updated_date, updated_start_datetime, updated_end_datetime)

                    st.success(f"🎉 Booking updated successfully for {updated_room} from {updated_start_time.strftime('%H:%M')} to {updated_end_time.strftime('%H:%M')}.")
                    #st.balloons()
            
            # Logout option for admin
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.success("Logged out successfully.")
        else:
            st.write("No bookings found in the system.")
