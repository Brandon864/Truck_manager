function validateTruckForm() {
    const truckId = document.forms["truckForm"]["truck_id"].value.trim();
    const type = document.forms["truckForm"]["type"].value.trim();
    const capacity = document.forms["truckForm"]["capacity"].value;

    if (truckId === "") {
        alert("Truck ID must be filled out");
        return false;
    }
    if (type === "") {
        alert("Truck type must be filled out");
        return false;
    }
    if (capacity <= 0) {
        alert("Capacity must be a positive number");
        return false;
    }
    return true;
}

function validateDriverForm() {
    const name = document.forms["driverForm"]["name"].value.trim();
    const phone = document.forms["driverForm"]["phone"].value.trim();
    const licenseNumber = document.forms["driverForm"]["license_number"].value.trim();
    const email = document.forms["driverForm"]["email"].value.trim();

    if (name === "") {
        alert("Name must be filled out");
        return false;
    }
    if (phone === "") {
        alert("Phone must be filled out");
        return false;
    }
    if (!/^\+?\d{10,15}$/.test(phone)) {
        alert("Phone number must be a valid number (10-15 digits, optional '+' prefix)");
        return false;
    }
    if (licenseNumber === "") {
        alert("License number must be filled out");
        return false;
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert("Please enter a valid email address");
        return false;
    }
    return true;
}

function validateDeliveryForm() {
    const pickup = document.forms["deliveryForm"]["pickup_location"].value.trim();
    const dropoff = document.forms["deliveryForm"]["dropoff_location"].value.trim();
    const startDatetime = document.forms["deliveryForm"]["start_datetime"].value;
    const truckId = document.forms["deliveryForm"]["truck_id"].value;
    const driverId = document.forms["deliveryForm"]["driver_id"].value;

    if (pickup === "") {
        alert("Pickup location must be filled out");
        return false;
    }
    if (dropoff === "") {
        alert("Drop-off location must be filled out");
        return false;
    }
    if (startDatetime === "") {
        alert("Start date and time must be selected");
        return false;
    }
    const now = new Date();
    const selectedDate = new Date(startDatetime);
    if (selectedDate < now) {
        alert("Start date and time must be in the future");
        return false;
    }
    if (truckId === "") {
        alert("A truck must be selected");
        return false;
    }
    if (driverId === "") {
        alert("A driver must be selected");
        return false;
    }
    return true;
}