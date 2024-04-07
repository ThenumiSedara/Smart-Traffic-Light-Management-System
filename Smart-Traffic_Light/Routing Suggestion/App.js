import React, {  useRef } from 'react';
import { StyleSheet, View, TextInput, Button, Alert } from 'react-native';
import MapView from 'react-native-maps';

const center = { latitude: 7.8731, longitude: 80.7718 };
const delta = { latitudeDelta: 5, longitudeDelta: 5 };

function App() {
  const originRef = useRef(null);
  const destinationRef = useRef(null);

  async function calculateRoute() {
    if (!originRef.current || !destinationRef.current) {
      Alert.alert('Error', 'Origin or destination not provided');
      return;
    }
  
    const origin = originRef.current.value;
    const destination = destinationRef.current.value;
  
    try {
      const apiKey = 'AIzaSyBBXd85H0dH35N0X6Ug9sU60_yMznOq6Js';
      const apiUrl = `https://maps.googleapis.com/maps/api/directions/json?origin=${origin}&destination=${destination}&key=${apiKey}`;
      const response = await fetch(apiUrl);
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const data = await response.json();
  
      if (data.status === 'OK') {
        setDirectionsResponse(data);
        const route = data.routes[0];
        setDistance(route.legs[0].distance.text);
        setDuration(route.legs[0].duration.text);
      } else {
        throw new Error(`Google Maps API error: ${data.error_message}`);
      }
    } catch (error) {
      Alert.alert('Error', `Failed to fetch directions: ${error.message}`);
      console.log(error)
    }
  }
  
  
  function clearRoute() {
    setDirectionsResponse(null);
    setDistance('');
    setDuration('');
    originRef.current.clear();
    destinationRef.current.clear();
  }

  return (
    <View style={styles.container}>
      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          region={{
            ...center,
            ...delta,
          }}
          maxZoomLevel={18}
          minZoomLevel={6}
          initialRegion={{
            ...center,
            ...delta,
          }}
        >
        </MapView>
      </View>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Start Location"
          ref={originRef}
        />
        <TextInput
          style={styles.input}
          placeholder="Destination"
          ref={destinationRef}
        />
        <View style={styles.buttonContainer}>
          <Button title="Calculate Route" onPress={calculateRoute} />
          <Button title="Clear Route" onPress={clearRoute} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  mapContainer: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  inputContainer: {
    padding: 20,
  },
  input: {
    marginBottom: 10,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 3,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
});

export default App;
