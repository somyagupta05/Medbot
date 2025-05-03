import os
import requests
import json
import streamlit as st
import math

# Get Mappls API key from environment variables
MAPPLS_API_KEY = os.getenv("MAPPLS_API_KEY", "")

def get_user_location():
    """
    Get the user's current location using browser geolocation
    
    Returns:
        tuple: (latitude, longitude) or None if location access is denied
    """
    # Only return location if explicitly set in session state
    if 'user_lat' in st.session_state and 'user_lng' in st.session_state:
        return (st.session_state.user_lat, st.session_state.user_lng)
    return None

def geocode_address(address):
    """
    Convert an address to coordinates using Google Geocoding API
    
    Args:
        address (str): Address to geocode
        
    Returns:
        tuple: (latitude, longitude) or None if geocoding fails
    """
    if not address:
        return None
    
    try:
        # Add India to the address if not specified
        if 'india' not in address.lower():
            search_address = f"{address}, India"
        else:
            search_address = address
            
        # Use Nominatim for geocoding (free and doesn't require API key)
        import geopy.geocoders
        from geopy.geocoders import Nominatim
        from geopy.extra.rate_limiter import RateLimiter
        
        # Create a geocoder instance
        geolocator = Nominatim(user_agent="emergency_ai_vision")
        # Add rate limiting to avoid hitting API limits
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        
        # Perform geocoding
        location = geocode(search_address)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            st.error(f"Could not find location: {address}")
            return None
            
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
        return None

def find_nearby_hospitals(radius_km=5):
    """
    Find nearby hospitals based on IITM Janakpuri location
    
    Args:
        radius_km (int): Search radius in kilometers
        
    Returns:
        list: List of hospital information dictionaries
    """
    # Set default coordinates to IITM Janakpuri
    default_lat = 28.610532
    default_lng = 77.101927
    
    # Get coordinates from user location if available, otherwise use IITM Janakpuri
    coords = get_user_location()
    if coords:
        lat, lng = coords
        st.success(f"Using your current location: {lat:.4f}, {lng:.4f}")
    else:
        lat, lng = default_lat, default_lng
        st.info("Using IITM Janakpuri location as reference point")
    
    try:
        # Updated hospital data focused around West Delhi
        sample_hospitals = [
            # Janakpuri Area
            {
                'name': 'Mata Chanan Devi Hospital',
                'address': 'C-1, Janakpuri, New Delhi, Delhi 110058',
                'lat': 28.6217,
                'lng': 77.0878,
                'phone': '011-2550 6242',
                'emergency': True,
                'specialties': ['Emergency Care', 'Multi-Specialty']
            },
            {
                'name': 'Orchid Hospital & Heart Center',
                'address': 'C-2/37, Janakpuri, New Delhi, Delhi 110058',
                'lat': 28.6198,
                'lng': 77.0910,
                'phone': '011-4575 5555',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Cardiology']
            },
            {
                'name': 'Janakpuri Super Specialty Hospital',
                'address': 'C-2B, Janakpuri, New Delhi, Delhi 110058',
                'lat': 28.6206,
                'lng': 77.0891,
                'phone': '011-2550 4090',
                'emergency': True,
                'specialties': ['Emergency Services', 'Super Specialty', 'Government Hospital']
            },
            {
                'name': 'Bensups Hospital',
                'address': 'B-1, Janakpuri, New Delhi, Delhi 110058',
                'lat': 28.6227,
                'lng': 77.0897,
                'phone': '011-4558 2000',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Critical Care']
            },
            {
                'name': 'Ayushman Hospital',
                'address': 'B-4, Janakpuri, New Delhi, Delhi 110058',
                'lat': 28.6212,
                'lng': 77.0883,
                'phone': '011-4558 7100',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Pediatrics']
            },
            
            # Vikaspuri Area
            {
                'name': 'Fortis Hospital Vikaspuri',
                'address': 'Vikaspuri, New Delhi, Delhi 110018',
                'lat': 28.6397,
                'lng': 77.0767,
                'phone': '011-4277 6222',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Critical Care']
            },
            {
                'name': 'Sehgal Neo Hospital',
                'address': 'Block A, Meera Bagh, Paschim Vihar, New Delhi, Delhi 110087',
                'lat': 28.6728,
                'lng': 77.1114,
                'phone': '011-4761 1111',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Critical Care']
            },
            {
                'name': 'Manipal Hospital',
                'address': 'Pankha Road, Dwarka, New Delhi, Delhi 110059',
                'lat': 28.6198,
                'lng': 77.0755,
                'phone': '011-4967 4967',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Trauma Center']
            },
            
            # Hari Nagar & Subhash Nagar Area
            {
                'name': 'Deen Dayal Upadhyay Hospital',
                'address': 'Hari Nagar, New Delhi, Delhi 110064',
                'lat': 28.6289,
                'lng': 77.1031,
                'phone': '011-2539 4302',
                'emergency': True,
                'specialties': ['Emergency Care', 'Government Hospital']
            },
            {
                'name': 'Metro Hospital',
                'address': 'Subhash Nagar, New Delhi, Delhi 110027',
                'lat': 28.6384,
                'lng': 77.1086,
                'phone': '011-4725 5555',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty']
            },
            
            # Rajouri Garden Area
            {
                'name': 'Kukreja Hospital',
                'address': 'Rajouri Garden, New Delhi, Delhi 110027',
                'lat': 28.6492,
                'lng': 77.1226,
                'phone': '011-4557 7777',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty']
            },
            
            # Extended Area Coverage (within 20km)
            {
                'name': 'Sir Ganga Ram Hospital',
                'address': 'Rajinder Nagar, New Delhi, Delhi 110060',
                'lat': 28.6403,
                'lng': 77.1892,
                'phone': '011-2575 7575',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Super Specialty']
            },
            {
                'name': 'BLK Super Specialty Hospital',
                'address': 'Pusa Road, New Delhi, Delhi 110005',
                'lat': 28.6447,
                'lng': 77.1789,
                'phone': '011-3040 3040',
                'emergency': True,
                'specialties': ['Emergency Services', 'Super Specialty', 'Trauma Center']
            },
            {
                'name': 'Maharaja Agrasen Hospital',
                'address': 'West Punjabi Bagh, New Delhi, Delhi 110026',
                'lat': 28.6651,
                'lng': 77.1324,
                'phone': '011-4760 5555',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Trauma Center']
            },
            {
                'name': 'Balaji Action Medical Institute',
                'address': 'Paschim Vihar, New Delhi, Delhi 110063',
                'lat': 28.6728,
                'lng': 77.1114,
                'phone': '011-4752 2222',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Cardiology']
            },
            {
                'name': 'Fortis Hospital Shalimar Bagh',
                'address': 'Shalimar Bagh, New Delhi, Delhi 110088',
                'lat': 28.7052,
                'lng': 77.1610,
                'phone': '011-4277 6222',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty', 'Trauma Center']
            },
            {
                'name': 'Max Super Specialty Hospital Shalimar Bagh',
                'address': 'Shalimar Bagh, New Delhi, Delhi 110088',
                'lat': 28.7156,
                'lng': 77.1553,
                'phone': '011-4055 4055',
                'emergency': True,
                'specialties': ['Emergency Services', 'Super Specialty', 'Trauma Center']
            },
            {
                'name': 'Saroj Super Specialty Hospital',
                'address': 'Rohini, New Delhi, Delhi 110085',
                'lat': 28.7099,
                'lng': 77.1183,
                'phone': '011-4707 7070',
                'emergency': True,
                'specialties': ['Emergency Services', 'Super Specialty', 'Critical Care']
            },
            {
                'name': 'Park Hospital',
                'address': 'Meera Bagh, Paschim Vihar, New Delhi, Delhi 110087',
                'lat': 28.6728,
                'lng': 77.1114,
                'phone': '011-4532 2222',
                'emergency': True,
                'specialties': ['Emergency Services', 'Multi-Specialty']
            },
            {
                'name': 'Aakash Healthcare Super Specialty Hospital',
                'address': 'Dwarka, New Delhi, Delhi 110075',
                'lat': 28.5937,
                'lng': 77.0420,
                'phone': '011-4677 7777',
                'emergency': True,
                'specialties': ['Emergency Services', 'Super Specialty', 'Trauma Center']
            }
        ]
        
        hospitals = []
        
        # Calculate distance to each hospital
        for hospital in sample_hospitals:
            # Calculate distance using Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            lat1, lon1 = math.radians(lat), math.radians(lng)
            lat2, lon2 = math.radians(hospital['lat']), math.radians(hospital['lng'])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            if distance <= radius_km:
                hospital_entry = hospital.copy()
                hospital_entry['distance'] = f"{distance:.1f} km"
                
                # Add Google Maps directions URL
                google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={hospital['lat']},{hospital['lng']}&travelmode=driving"
                hospital_entry['directions_url'] = google_maps_url
                
                hospitals.append(hospital_entry)
        
        # Sort hospitals by distance
        hospitals.sort(key=lambda h: float(h['distance'].split()[0]))
        
        if not hospitals:
            st.warning(f"No hospitals found within {radius_km} km of the specified location.")
        else:
            st.success(f"Found {len(hospitals)} hospitals within {radius_km} km.")
        
        return hospitals
    
    except Exception as e:
        st.error(f"Error finding nearby hospitals: {str(e)}")
        return []

def get_hospital_details(eloc):
    """
    Get detailed information about a hospital using Mappls place detail API
    
    Args:
        eloc (str): Mappls eLoc code of the hospital
        
    Returns:
        dict: Detailed hospital information
    """
    if not eloc:
        return None
    
    try:
        # Prepare the API URL for Mappls place detail
        url = f"https://apis.mappls.com/advancedmaps/v1/{MAPPLS_API_KEY}/place_detail?place_id={eloc}"
        
        # Make the API request
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'result' in result:
                details = result['result']
                
                # Get phone number from contact information
                phone = "N/A"
                if 'contactDetails' in details and 'telephone' in details['contactDetails']:
                    phone = details['contactDetails']['telephone']
                
                hospital_details = {
                    'name': details.get('name', 'Unknown'),
                    'address': details.get('address', 'Address not available'),
                    'phone': phone,
                    'website': details.get('website', None),
                    'rating': details.get('averageRating', None)
                }
                
                # Get opening hours if available
                if 'openingHours' in details:
                    hospital_details['opening_hours'] = details['openingHours'].get('weekdayText', [])
                
                return hospital_details
            else:
                print("Mappls Place Detail API error: No results found")
                return None
        else:
            print(f"Mappls Place Detail request error: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Exception in get_hospital_details: {e}")
        return None
