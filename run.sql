-- Question 1
SELECT
    title, COUNT(title) as watchCount
FROM
    watch_history
GROUP BY
    title
ORDER BY
    watchCount DESC
FETCH FIRST 10 ROWS ONLY;

-- Question 2
SELECT
    s.channelName, COUNT(*) as watchCount
FROM
    watch_history wh
INNER JOIN
    subscriptions s
ON
    s.channelName = wh.channelName
GROUP BY
    s.channelName
ORDER BY
    watchCount DESC;

-- Question 3
SELECT
    TO_CHAR(watchDate, 'YYYY-MM-DD') as watchDate
FROM
    watch_history
GROUP BY
    TO_CHAR(watchDate, 'YYYY-MM-DD')
ORDER BY
    COUNT(watchDate) DESC
FETCH FIRST 1 ROWS ONLY;

-- Question 4
SELECT
    COUNT(*) / COUNT(DISTINCT TO_CHAR(watchDate, 'YYYY-MM-DD'))
    as avg_watched_videos_per_day
FROM
    watch_history;

-- Question 5
SELECT
    searchQuery, COUNT(searchQuery) as searchCount
FROM
    search_history
WHERE
    ADD_MONTHS(searchDate, 12) > CURRENT_DATE
GROUP BY    
    searchQuery
ORDER BY
    searchCount DESC

-- Question 6
SELECT
    wh.channelName, COUNT(wh.videoURL) AS watchedVideos
FROM    
    watch_history wh
LEFT JOIN
    subscriptions s
ON
    wh.channelName = s.channelName
WHERE
    s.channelURL IS NULL
GROUP BY
    wh.channelName
ORDER BY
    watchedVideos DESC
FETCH FIRST 5 ROWS ONLY;

-- Question 7
SELECT
    COUNT(*) /
    COUNT(DISTINCT TO_CHAR(searchDate, 'YYYY-MM-DD')) as searchCount
FROM
    search_history;

-- Question 8
SELECT
    sh.searchQuery, COUNT(*) AS watchCount
FROM
    search_history sh,
    watch_history wh
WHERE
    sh.searchDate <= wh.watchDate
GROUP BY
    TO_CHAR(sh.searchDate, 'YYYY-MM-DD'),
    sh.searchQuery
ORDER BY
    watchCount DESC;

-- Question 9
SELECT
    TO_CHAR(watchDate, 'YYYY-MM-DD') as watchDate,
    SUM(NVL(length, 0)) AS watchSeconds
FROM
    watch_history
GROUP BY
    TO_CHAR(watchDate, 'YYYY-MM-DD')
ORDER BY
    watchSeconds DESC
FETCH FIRST 5 ROWS ONLY;

-- Question 10.a
SELECT
    title, channelName, COUNT(*) AS views
FROM
    watch_history
WHERE
    watchDate <= TO_TIMESTAMP('2020-05-15', 'YYYY-MM-DD')
GROUP BY
    title, channelName
ORDER BY
    views DESC
FETCH FIRST 5 ROWS ONLY;

-- Question 10.b
SELECT
    title, channelName, COUNT(*) AS views
FROM
    watch_history
WHERE
    watchDate > TO_TIMESTAMP('2020-05-15', 'YYYY-MM-DD')
GROUP BY
    title, channelName
ORDER BY
    views DESC
FETCH FIRST 5 ROWS ONLY;