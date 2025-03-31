library(dplyr)

df = read.csv('/Users/siva/Desktop/combined.csv')



#admision#
table(df$source)
#age
mean_TBI = df %>%
  filter(source == 'TBI') %>%
  pull(AGE) %>% 
  mean(na.rm = TRUE)
mean_TBI
mean_SCI = df %>%
  filter(source == 'SCI') %>%
  pull(AGE) %>% 
  mean(na.rm = TRUE)
mean_SCI
mean_Both = df %>%
  filter(source == 'Both') %>%
  pull(AGE) %>% 
  mean(na.rm = TRUE)
mean_Both


model = aov(AGE ~ source, data = df_clean)
summary(model)

#sex
df %>% filter(source == "TBI" & FEMALE == "Male") %>% count()
df %>% filter(source == "SCI" & FEMALE == "Male") %>% count()
df %>% filter(source == "Both" & FEMALE == "Male") %>% count()

df_male <- df %>%
  filter(FEMALE == "Male") %>%
  count(source)
df_male

chisq_test <- chisq.test(df_male$n)
chisq_test


df %>% filter(source == "TBI" & FEMALE == "Female") %>% count()
df %>% filter(source == "SCI" & FEMALE == "Female") %>% count()
df %>% filter(source == "Both" & FEMALE == "Female") %>% count()

df_female <- df %>%
  filter(FEMALE == "Female") %>%
  count(source)
df_female

chisq_test <- chisq.test(df_female$n)
chisq_test

#race

df_white <- df %>%
  filter(RACE == "White") %>%
  count(source)
df_white

chisq_test <- chisq.test(df_white$n)
chisq_test

#Black


df_black <- df %>%
  filter(RACE == "Black") %>%
  count(source)
df_black$n

chisq_test <- chisq.test(df_black$n)
chisq_test


#Hispanic


df_His <- df %>%
  filter(RACE == "Hispanic") %>%
  count(source)

df_His

chisq_test <- chisq.test(df_His$n)

chisq_test


#Asian

df_Asia <- df %>%
  filter(RACE == "Asian or Pacific Islander") %>%
  count(source)
df_Asia

chisq_test <- chisq.test(df_Asia$n)

chisq_test


#Native American

df_native <- df %>%
  filter(RACE == "Native American") %>%
  count(source)
df_native

chisq_test <- chisq.test(df_native$n)

chisq_test

#Other


df_other <- df %>%
  filter(RACE == "Other") %>%
  count(source)
df_other

chisq_test <- chisq.test(df_other$n)

chisq_test

#N/A  not working


df_na <- df %>%
  filter(is.na(RACE)) %>%
  count(source)
df_na

df_na <- chisq.test(df_na$n)

chisq_test

#Length of stay

mean_TBI = df %>%
  filter(source == 'TBI') %>%
  pull(LOS) %>% 
  mean(na.rm = TRUE)
mean_TBI

mean_SCI = df %>%
  filter(source == 'SCI') %>%
  pull(LOS) %>% 
  mean(na.rm = TRUE)
mean_SCI

mean_Both = df %>%
  filter(source == 'Both') %>%
  pull(LOS) %>% 
  mean(na.rm = TRUE)
mean_Both

model= aov(LOS~source, df)
summary(model)

#TOTCHG

mean_TBI = df %>%
  filter(source == 'TBI') %>%
  pull(TOTCHG) %>% 
  mean(na.rm = TRUE)
mean_TBI

mean_SCI = df %>%
  filter(source == 'SCI') %>%
  pull(TOTCHG) %>% 
  mean(na.rm = TRUE)
mean_SCI

mean_Both = df %>%
  filter(source == 'Both') %>%
  pull(TOTCHG) %>% 
  mean(na.rm = TRUE)
mean_Both

model= aov(TOTCHG~source, df)
summary(model)


#Avg PRDAY1
mean_TBI = df %>%
  filter(source == 'TBI') %>%
  pull(PRDAY1) %>% 
  mean(na.rm = TRUE)
mean_TBI

mean_SCI = df %>%
  filter(source == 'SCI') %>%
  pull(PRDAY1) %>% 
  mean(na.rm = TRUE)
mean_SCI

mean_Both = df %>%
  filter(source == 'Both') %>%
  pull(PRDAY1) %>% 
  mean(na.rm = TRUE)
mean_Both

model= aov(PRDAY1~source, df)
summary(model)

#Died
df_Died <- df %>%
  filter(DIED == 'Died') %>%
  count(source)
df_Died$n

chisq_test <- chisq.test(df_Died$n)
chisq_test

#Not dead
df_NDied <- df %>%
  filter(DIED == 'Did not die') %>%
  count(source)
df_NDied$n

chisq_test <- chisq.test(df_NDied$n)
chisq_test
