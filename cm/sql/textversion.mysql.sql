ALTER TABLE cm_textversion ADD FULLTEXT(content, title);

----- set stop word file
-- SET  ft_stopword_file = ''
----- set min word (default is 4)
-- SET  ft_min_word_len = 2
----- repair to take changes into account
-- REPAIR TABLE cm_textversion QUICK;
