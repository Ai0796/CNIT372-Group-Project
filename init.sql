/*
    This file sets up all the tables in preparation for the importing of YouTube data
*/

-- Create the tables
CREATE TABLE Subscriptions (
    channelURL VARCHAR2(255) NOT NULL,
    channelId VARCHAR2(255) NOT NULL,
    channelName VARCHAR2(255) NOT NULL,
    PRIMARY KEY (channelURL)
);

CREATE TABLE WatchHistory (
    videoTitle VARCHAR2(255) NOT NULL,
    videoURL VARCHAR2(255) NOT NULL,
    channelName VARCHAR2(255) NOT NULL,
    channelURL VARCHAR2(255) NOT NULL,
    watchDate TIMESTAMP NOT NULL,
    genre VARCHAR(255) NOT NULL,
    PRIMARY KEY (videoId, watchTime)
);

CREATE TABLE SearchHistory (
    searchQuery VARCHAR2(255) NOT NULL,
    searchDate TIMESTAMP NOT NULL,
    PRIMARY KEY (searchQuery, searchDate)
);

CREATE TABLE Comments (
    videoURL VARCHAR2(255) NOT NULL,
    comment VARCHAR2(255) NOT NULL, 
    /*  
        While comments can be longer than 255 characters, 
        this is a reasonable limit for this project
    */
    commentDate TIMESTAMP NOT NULL,
)