CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
	Time date,
	Vaccine varchar(255) REFERENCES Vaccines(Name),
	AppointmentID int IDENTITY(1, 1),
	Caregiver varchar(255),
	Patient varchar(255) REFERENCES Patients(Username),
	PRIMARY KEY (AppointmentID),
	FOREIGN KEY (Time, Caregiver) REFERENCES Availabilities(Time, Username)
);
