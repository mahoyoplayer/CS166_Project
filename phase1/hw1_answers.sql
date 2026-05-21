CREATE TABLE Employee (
    ssn CHAR(10),
    union_mem_no INTEGER,
    PRIMARY KEY (ssn)
);

CREATE TABLE Technician (
    ssn CHAR(10),
    salary INTEGER,
    last_name CHAR(20),
    address CHAR(20),
    phone_num CHAR(10),
    PRIMARY KEY (ssn),
    FOREIGN KEY (ssn) REFERENCES Employee(ssn)
);

CREATE TABLE Traffic_Controller (
    ssn CHAR(10),
    age INTEGER,
    years_exp INTEGER,
    PRIMARY KEY (ssn),
    FOREIGN KEY (ssn) REFERENCES Employee(ssn)
);

CREATE TABLE Exam (
    level CHAR(10),
    duration INTEGER,
    date CHAR(20),
    PRIMARY KEY (level)
);

CREATE TABLE Passed (
    level CHAR(10),
    ssn CHAR(10) NOT NULL,
    PRIMARY KEY (level, ssn),
    FOREIGN KEY (ssn) REFERENCES Traffic_Controller(ssn),
    FOREIGN KEY (level) REFERENCES Exam(level)
);

CREATE TABLE Model (
    model_no INTEGER,
    seat_capacity INTEGER,
    fuel CHAR(10),
    weight REAL,
    PRIMARY KEY (model_no)
);

CREATE TABLE Can_Fix (
    model_no INTEGER NOT NULL,
    ssn CHAR(10) NOT NULL,
    PRIMARY KEY (model_no, ssn),
    FOREIGN KEY (model_no) REFERENCES Model(model_no),
    FOREIGN KEY (ssn) REFERENCES Technician(ssn)
);

CREATE TABLE AirplaneType (
    reg_no INTEGER,
    company CHAR(20),
    model_no INTEGER NOT NULL,
    PRIMARY KEY (reg_no),
    FOREIGN KEY (model_no) REFERENCES Model(model_no)
);

CREATE TABLE Test (
    FAA_no CHAR(10),
    name CHAR(20),
    max_score INTEGER,
    PRIMARY KEY (FAA_no)
);

CREATE TABLE Test_Info (
    ssn CHAR(10),
    FAA_no CHAR(10),
    reg_no INTEGER,
    hours INTEGER,
    date CHAR(20),
    score INTEGER,
    PRIMARY KEY (ssn, FAA_no, reg_no),
    FOREIGN KEY (ssn) REFERENCES Technician(ssn),
    FOREIGN KEY (FAA_no) REFERENCES Test(FAA_no),
    FOREIGN KEY (reg_no) REFERENCES AirplaneType(reg_no)
);