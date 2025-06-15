-- @block
DROP TABLE playlists_DB;

-- @block
CREATE TABLE playlists_DB(
    playlistName VARCHAR(255) PRIMARY KEY,
    createdOn DATE
);

-- @block
INSERT INTO playlists_DB(playlistName, createdOn)
VALUES ("Default_Playlist", CURRENT_DATE)

-- @block
SELECT * FROM playlists_DB

-- @block
-- CREATE TABLE Users(
--     userID INT PRIMARY KEY AUTO_INCREMENT,
--     userName VARCHAR(255) NOT NULL UNIQUE,
--     userPwd VARCHAR(255),
--     fullName VARCHAR(255),
--     lastLogin DATETIME(0) DEFAULT CURRENT_TIMESTAMP,
--     userCreatedOn DATETIME(0) DEFAULT CURRENT_TIMESTAMP
-- );

-- -- @block
-- INSERT INTO Users(userName,userPwd,fullName)
-- VALUES (
--     'adminAbishek3',
--     '129198513',
--     'Abishek Ponpathirkootam Srikanth'
-- );

-- -- @block
-- SELECT * FROM users ORDER BY userCreatedOn DESC LIMIT 10
-- -- UPDATE Users
-- -- SET lastLogin = CURRENT_TIMESTAMP
-- -- WHERE userName = "adminAbishek";
