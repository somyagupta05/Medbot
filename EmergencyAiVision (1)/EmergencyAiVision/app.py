import streamlit as st
import os
import io
from PIL import Image
import time
import base64
from utils.image_processing import preprocess_image
from utils.gemini_api import analyze_injury, generate_first_aid, get_chatbot_response
from utils.location_services import find_nearby_hospitals

# Set page configuration
st.set_page_config(
    page_title="Aidly",
    page_icon="🚑",
    layout="wide"
)

# Initialize session state variables
if 'image' not in st.session_state:
    st.session_state.image = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'first_aid' not in st.session_state:
    st.session_state.first_aid = None
if 'severity' not in st.session_state:
    st.session_state.severity = None
if 'hospitals' not in st.session_state:
    st.session_state.hospitals = None
if 'chatbot_history' not in st.session_state:
    st.session_state.chatbot_history = []
if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = 28.610532  # Default to IITM Janakpuri
if 'user_lng' not in st.session_state:
    st.session_state.user_lng = 77.101927  # Default to IITM Janakpuri

# Header
st.title("🚑 Aidly")
st.markdown("**Emergency medical guidance using AI**")

# Sidebar content
with st.sidebar:
    # About Section with minimal styling
    st.markdown("""
        # <span style='color: #FF4B4B; font-size: 24px;'>🚑 About Aidly</span>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add space
    st.markdown("### What is Aidly?")
    
    st.markdown("""
        <p style='margin: 15px 0 25px 0; line-height: 1.6;'>
        Aidly is your AI-powered emergency medical assistant, providing immediate guidance for injuries using advanced computer vision and artificial intelligence.
        </p>
    """, unsafe_allow_html=True)
    
    # Key Features section
    st.markdown("""
        <div style='background-color: #e8f4f9; padding: 20px; border-radius: 10px; margin: 25px 0;'>
            <h3 style='margin-bottom: 15px;'>Key Features</h3>
            <div style='line-height: 2.2;'>
                • 📸 Upload or capture injury images<br>
                • 🤖 Get AI-powered analysis<br>
                • 🏥 Locate nearby hospitals<br>
                • 💬 Chat with AI for guidance<br>
                • ⚠️ Severity assessment<br>
                • 📋 First aid instructions
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Emergency Numbers section
    st.markdown("""
        <div style='background-color: #ffe8ec; padding: 20px; border-radius: 10px; margin: 25px 0;'>
            <h3 style='margin-bottom: 15px;'>Emergency Numbers</h3>
            <div style='line-height: 2.2;'>
                • 🚑 Ambulance: 108<br>
                • 🆘 National Emergency: 112<br>
                • 👶 Pregnancy: 102<br>
                • 👮 Police: 100<br>
                • 🚒 Fire: 101
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer section
    st.markdown("""
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; margin: 25px 0;'>
            <h3 style='margin-bottom: 15px;'>⚠️ Important Disclaimer</h3>
            <p style='color: #cc0000; margin-bottom: 15px; line-height: 1.6;'>
                This app provides first aid guidance only. Always seek professional medical help in emergencies.
            </p>
            <p style='color: #666666; font-size: 0.9em; line-height: 1.6;'>
                The AI analysis and recommendations are meant to assist, not replace, professional medical advice.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Main content
tab1, tab2, tab3 = st.tabs(["📸 Analyze Injury", "🏥 Find Hospitals", "💬 Emergency Chat"])

# Tab 1: Analyze Injury
with tab1:
    st.header("Upload or capture an image of the injury")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            try:
                # Check file size (200MB limit)
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
                if file_size > 200:
                    st.error("File size exceeds 200MB limit")
                else:
                    # Reset the file pointer
                    uploaded_file.seek(0)
                    # Open and process image
                    image = Image.open(uploaded_file)
                    # Convert to RGB if needed
                    if image.mode in ('RGBA', 'LA', 'P'):
                        image = image.convert('RGB')
                    # Store in session state
                    st.session_state.image = image
                    # Display image
                    st.image(image, caption="Uploaded Image", width=400)
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                print(f"Detailed error: {str(e)}")  # For debugging
    
    with col2:
        camera_photo = st.camera_input("Or take a photo")
        if camera_photo is not None:
            try:
                image = Image.open(camera_photo)
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                st.session_state.image = image
            except Exception as e:
                st.error(f"Error processing camera photo: {str(e)}")
    
    analyze_button = st.button("Analyze Injury", type="primary", use_container_width=True)
    
    if analyze_button and st.session_state.image is not None:
        with st.spinner("Analyzing the injury..."):
            st.session_state.loading = True
            
            # Preprocess the image
            preprocessed_img = preprocess_image(st.session_state.image)
            
            # Analyze the injury using Gemini API
            analysis_result = analyze_injury(preprocessed_img)
            st.session_state.analysis_result = analysis_result
            
            # Generate severity score (1-10)
            severity = int(analysis_result.get('severity_score', 5))
            st.session_state.severity = severity
            
            # Generate first aid instructions
            first_aid = generate_first_aid(analysis_result)
            st.session_state.first_aid = first_aid
            
            st.session_state.loading = False
    
    # Display results if available
    if st.session_state.analysis_result:
        st.markdown("---")
        st.header("Analysis Results")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Injury Assessment")
            st.markdown(f"**Identified Condition:** {st.session_state.analysis_result.get('condition', 'Unknown')}")
            
            # Display severity with appropriate color
            severity = st.session_state.severity
            severity_color = "green"
            if severity > 3:
                severity_color = "orange"
            if severity > 7:
                severity_color = "red"
            
            st.markdown(f"**Severity Score:** <span style='color:{severity_color};font-size:24px;font-weight:bold;'>{severity}/10</span>", unsafe_allow_html=True)
            
            if severity > 7:
                st.error("⚠️ HIGH SEVERITY: Seek immediate medical attention!")
        
        with col2:
            st.subheader("First Aid Instructions")
            st.markdown(st.session_state.first_aid)
        
        # For high severity cases, automatically show hospital information
        if severity > 7:
            st.markdown("---")
            st.subheader("⚠️ Nearby Hospitals")
            st.info("Please enable location services to find nearby hospitals")
            
            if st.button("Find Nearby Hospitals"):
                with st.spinner("Locating nearby hospitals..."):
                    hospitals = find_nearby_hospitals()
                    st.session_state.hospitals = hospitals
            
            if st.session_state.hospitals:
                for hospital in st.session_state.hospitals[:3]:
                    st.markdown(f"**{hospital['name']}**  \n{hospital['address']}  \nDistance: {hospital['distance']}  \nPhone: {hospital.get('phone', 'N/A')}")
                    if 'mappls_directions_url' in hospital:
                        st.markdown(f"[Get Directions (Mappls)]({hospital['mappls_directions_url']})")
                    elif 'directions_url' in hospital:
                        st.markdown(f"[Get Directions (Google Maps)]({hospital['directions_url']})")
                    st.markdown("---")

# Tab 2: Find Hospitals
with tab2:
    st.header("Find Nearby Hospitals")
    
    # Location access component
    st.info("Please allow location access to find nearby hospitals. If location access is denied, IITM Janakpuri will be used as the reference point.")
    
    # Add JavaScript to get user's location
    location_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Success callback
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Send the coordinates to Streamlit
                    fetch("/_stcore/streamlit_message", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            type: "streamlit:customEvent",
                            payload: {
                                type: "user_location_captured",
                                data: { lat: lat, lng: lng }
                            }
                        })
                    });
                    
                    document.getElementById('location-status').innerText = "✅ Location detected: " + lat.toFixed(4) + ", " + lng.toFixed(4);
                },
                function(error) {
                    // Error callback
                    let errorMessage = "Using IITM Janakpuri location as reference point. Error: ";
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage += "Location permission denied.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage += "Location information unavailable.";
                            break;
                        case error.TIMEOUT:
                            errorMessage += "Location request timed out.";
                            break;
                        default:
                            errorMessage += "Unknown error.";
                            break;
                    }
                    document.getElementById('location-status').innerText = errorMessage;
                }
            );
        } else {
            document.getElementById('location-status').innerText = "Using IITM Janakpuri location (Geolocation not supported by browser)";
        }
    }
    </script>
    
    <div>
        <button onclick="getLocation()" style="background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">
            Get My Location
        </button>
        <div id="location-status" style="margin-top: 8px; font-style: italic;">Click button to detect location</div>
    </div>
    """
    
    st.components.v1.html(location_js, height=100)
    
    # Handle custom event for location
    if st.session_state.get('user_location_captured'):
        location_data = st.session_state.user_location_captured
        st.session_state.user_lat = location_data['lat']
        st.session_state.user_lng = location_data['lng']
        st.session_state.user_location_captured = None  # Reset after handling
    
    col1, col2 = st.columns(2)
    
    with col2:
        search_radius = st.slider(
            "Search radius (km)",
            min_value=1,
            max_value=20,
            value=5,
            help="Adjust the radius to find hospitals within this distance"
        )
    
    if st.button("Search Hospitals", use_container_width=True):
        with st.spinner("Searching for nearby hospitals..."):
            hospitals = find_nearby_hospitals(radius_km=search_radius)
            st.session_state.hospitals = hospitals
    
    if st.session_state.hospitals:
        st.subheader("Nearest Medical Facilities")
        
        # Display map
        try:
            import folium
            from streamlit_folium import folium_static
            from folium import plugins
            
            # Get user's location
            user_lat = st.session_state.user_lat
            user_lng = st.session_state.user_lng
            
            # Create the map centered on user location
            m = folium.Map(
                location=[user_lat, user_lng],
                zoom_start=13,
                tiles="OpenStreetMap"
            )
            
            # Add user location marker with a custom icon
            folium.Marker(
                [user_lat, user_lng],
                popup="Your Location",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(m)
            
            # Create a feature group for hospitals
            hospital_group = folium.FeatureGroup(name="Hospitals")
            
            # Add hospital markers
            for hospital in st.session_state.hospitals:
                # Create popup content with HTML formatting
                popup_html = f"""
                <div style="width: 250px; padding: 10px;">
                    <h4 style="color: #FF4B4B; margin: 0 0 10px 0;">{hospital['name']}</h4>
                    <p style="margin: 5px 0;"><b>Distance:</b> {hospital['distance']}</p>
                    <p style="margin: 5px 0;"><b>Phone:</b> {hospital.get('phone', 'N/A')}</p>
                    <p style="margin: 5px 0;"><b>Address:</b> {hospital['address']}</p>
                    <div style="margin-top: 10px;">
                        <a href="{hospital['directions_url']}" target="_blank" style="color: #FF4B4B;">Get Directions</a>
                    </div>
                </div>
                """
                
                # Add hospital marker
                folium.Marker(
                    location=[hospital['lat'], hospital['lng']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color="red", icon="plus", prefix='fa'),
                    tooltip=hospital['name']
                ).add_to(hospital_group)
            
            # Add the hospital group to the map
            hospital_group.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add fullscreen button
            plugins.Fullscreen().add_to(m)
            
            # Fit bounds to include all markers
            bounds = [[hospital['lat'], hospital['lng']] for hospital in st.session_state.hospitals]
            bounds.append([user_lat, user_lng])
            m.fit_bounds(bounds)
            
            # Create columns for map and list view
            map_col, list_col = st.columns([2, 1])
            
            with map_col:
                # Display the map with a fixed height
                st.write("### Interactive Map")
                folium_static(m, width=800, height=500)
            
            with list_col:
                st.markdown("""
                <div style="background-color: #FF4B4B; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h2 style="color: white; margin: 0; text-align: center;">Nearby Hospitals</h2>
                </div>
                """, unsafe_allow_html=True)
                
                if not st.session_state.hospitals:
                    st.info("No hospitals found within the selected radius. Try increasing the search radius.")
                else:
                    for i, hospital in enumerate(st.session_state.hospitals):
                        with st.expander(f"{i+1}. {hospital['name']}", expanded=True):
                            st.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <h4 style="color: #FF4B4B; margin: 0 0 10px 0;">{hospital['name']}</h4>
                                <p style="margin: 5px 0;"><b>📍 Distance:</b> {hospital['distance']}</p>
                                <p style="margin: 5px 0;"><b>📞 Phone:</b> {hospital.get('phone', 'N/A')}</p>
                                <p style="margin: 5px 0;"><b>🏥 Address:</b> {hospital['address']}</p>
                                <p style="margin: 5px 0;"><b>⚕️ Specialties:</b> {', '.join(hospital.get('specialties', []))}</p>
                                {f"<p style='margin: 5px 0;'><b>🚨 Emergency Services:</b> Available</p>" if hospital.get('emergency', False) else ""}
                                <div style="margin-top: 10px;">
                                    <a href="{hospital['directions_url']}" target="_blank" style="background-color: #FF4B4B; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">Get Directions</a>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Could not display map: {str(e)}")
            # Print detailed error for debugging
            import traceback
            st.write("Detailed error:")
            st.code(traceback.format_exc())

# Tab 3: Emergency Chat
with tab3:
    st.header("Emergency Guidance Chat")
    st.info("Ask questions about first aid or emergency procedures")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your question here"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response with loading animation
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 Thinking...")
            
            try:
                # Get the actual response
                response = get_chatbot_response(prompt)
                
                # Display response with typing effect
                full_response = ""
                for chunk in response.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.02)  # Slightly faster typing speed
                
                # Final display without cursor
                message_placeholder.markdown(response)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Error getting AI response: {str(e)}"
                message_placeholder.error(error_msg)
                import traceback
                st.error(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>⚠️ <b>IMPORTANT:</b> This app provides first aid guidance only. Always seek professional medical help in emergencies.</p>
        <p>© 2023 Aidly | Indian Emergency Services: 112 (National Emergency), 108 (Ambulance), 102 (Pregnancy)</p>
    </div>
    """, 
    unsafe_allow_html=True
)
