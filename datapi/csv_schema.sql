DROP TABLE IF EXISTS dataset;

CREATE TABLE dataset ( 
	tdate TEXT,
	channel TEXT,
	country TEXT,
	os TEXT,
	impressions INTEGER,
	clicks INTEGER,
	installs INTEGER,
	spend REAL,
	revenue REAL
);

