import joblib
import pandas as pd

considered_features=['statuses_count','followers_count','favourites_count', 'friends_count', 'listed_count',
                   'default_profile', 'profile_use_background_image', 'verified', 'age', 'name', 'screen_name',
                   'description']

dic_snscrape_to_API={'username' : 'name', 'displayname' : 'screen_name', 'created' : 'created_at', 'followersCount' : 'followers_count', 'friendsCount' : 'friends_count', 'statusesCount' : 'statuses_count',
                  'favouritesCount' : 'favourites_count', 'listedCount' : 'listed_count', 'profileBannerUrl' : 'profile_banner_url', 'description' : 'description', }

model = joblib.load('random_forest.joblib')


def age(date):
    u = pd.Timestamp(date, tz=None)
    u = u.tz_convert(None)
    return (pd.Timestamp.today() - u).days + 1


def nbdigits(string):
    return sum(c.isdigit() for c in string)


def augmentdf(df):
    output = pd.DataFrame.copy(df)
    output["tweet_frequence"] = df["statuses_count"] / df["age"]
    output["followers_growth_rate"] = df["followers_count"] / df["age"]
    output["friends_growth_rate"] = df["friends_count"] / df["age"]
    output["favourites_growth_rate"] = df["favourites_count"] / df["age"]
    output["listed_growth_rate"] = df["listed_count"] / df["age"]
    output["friends_followers_ratio"] = df["friends_count"] / (
        df["followers_count"] + 1
    )
    output["followers_friend_ratio"] = df["followers_count"] / (df["friends_count"] + 1)
    output["name_length"] = df["name"].apply(len)
    output["screenname_length"] = df["screen_name"].apply(len)
    output["name_digits"] = df["name"].apply(nbdigits)
    output["screen_name_digits"] = df["screen_name"].apply(nbdigits)
    output["description_length"] = df["description"].apply(len)
    return output


def proba_bot(dataframe):
    dataframe.rename(columns=dic_snscrape_to_API, inplace=True)
    dataframe["profile_use_background_image"] = dataframe['profile_banner_url'].apply(lambda x : True if x else False)
    dataframe["default_profile"] = dataframe['description'].apply(lambda x : False if x=="" else True)
    dataframe["age"] = dataframe["created_at"].apply(age)
    features = dataframe[considered_features]
    features = augmentdf(features)
    features = features.drop(columns=["description", "name", "screen_name"])
    bot_score = model.predict_proba(features)[:,1]
    
    return bot_score