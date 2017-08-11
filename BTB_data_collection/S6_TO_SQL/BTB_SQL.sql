
USE biotoolbay;

 CREATE TABLE journals(
    id INT NOT NULL,
    name VARCHAR(60),
    URL_main VARCHAR(250),
    URL_logo VARCHAR(250),
    PRIMARY KEY (id)
);

CREATE TABLE articles (
    id INT NOT NULL,
    link VARCHAR(250),
    doi VARCHAR(50),
    abstract TEXT,
    title TEXT,
    authors TEXT,
    topics TEXT,
    tag TEXT,
    citation_link TEXT,
    article_references TEXT,
    date DATE,
    additional_info VARCHAR(50),
    journal_fk INT,
    main BOOLEAN,
    PRIMARY KEY (id),
    FOREIGN KEY (journal_fk) REFERENCES journals(id)
);

CREATE TABLE altmetrics(
    score INT NOT NULL,
    badge_link VARCHAR(150),
    PRIMARY KEY(score)
);

CREATE TABLE tools (
    id INT NOT NULL,
    homepage VARCHAR(250),
    name_tool VARCHAR(60),
    article_fk INT,
    PRIMARY KEY (id),
    FOREIGN KEY (article_fk) REFERENCES articles(id)
);


CREATE TABLE metrics(
    id INT NOT NULL,
    views INT,
    relative_views INT,
    citations INT,
    citations_per_year INT,
    altmetric_fk INT,
    PRIMARY KEY (id),
	FOREIGN KEY (altmetric_fk) REFERENCES altmetrics(score)
); 


CREATE TABLE tool_graphing (
    id INT NOT NULL,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    x_2d FLOAT,
    y_2d FLOAT,
    size_views INT,
    color_citations INT,
    tool_fk INT,
    PRIMARY KEY (id),
    FOREIGN KEY (tool_fk) REFERENCES tools(id)
);



CREATE TABLE similar_tools (
    id INT NOT NULL,
    main_tool INT,
    similar_tool_fk INT,
    similarity FLOAT,
    rank INT,
    PRIMARY KEY (id),
    FOREIGN KEY (similar_tool_fk) REFERENCES tools(id)
);


CREATE TABLE related_articles (
    id INT NOT NULL,
    tool_id INT,
    related_article_fk INT,
    PRIMARY KEY (id),
    FOREIGN KEY (related_article_fk) REFERENCES articles(id)
);

CREATE TABLE keywords (
    id INT NOT NULL,
    keyword VARCHAR(250),
    PRIMARY KEY (id)
);

CREATE TABLE tagmap (
    id INT NOT NULL,
    tool_fk INT,
    tag_fk INT,
    PRIMARY KEY (id),
    FOREIGN KEY (tool_fk) REFERENCES tools(id),
    FOREIGN KEY (tag_fk) REFERENCES keywords(id)
);