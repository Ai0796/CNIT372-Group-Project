DROP TABLE comments;
DROP TABLE search_history;
DROP TABLE watch_history;
DROP TABLE subscriptions;

CREATE TABLE comments(
    commentURL VARCHAR2(150) PRIMARY KEY,
    videoURL VARCHAR2(100),
    commentText VARCHAR2(255),
    commentDate TIMESTAMP
);

CREATE TABLE watch_history(
    title VARCHAR2(100),
    videoURL VARCHAR2(100),
    channelName VARCHAR2(30),
    channelURL VARCHAR2(100),
    watchDate TIMESTAMP NOT NULL,
    length INT,
    PRIMARY KEY (videoURL, watchDate)
);

CREATE TABLE search_history(
    searchQuery VARCHAR2(255) NOT NULL,
    searchDate TIMESTAMP NOT NULL,
    searchURL VARCHAR2(255),
    PRIMARY KEY (searchURL, searchDate)
);

CREATE TABLE subscriptions(
    channelId VARCHAR2(30) PRIMARY KEY,
    channelName VARCHAR2(30),
    channelURL VARCHAR2(100)
);
