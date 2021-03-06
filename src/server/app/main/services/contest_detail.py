from app.main import db
from time import gmtime, strftime
import datetime
# from app import User

from app.main.models.ContestsModel import ContestsModel
from app.main.models.ChallengesModel import ChallengesModel
from app.main.models.ContestsChallengesModel import contests_challenges
import time


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


def find_by_name(cls, contest_name):
    """
        Find by contest Name
        :param contest_name
        :return object containing all contest details
    """
    return cls.query.filter_by(contest_name=contest_name)


def get_contests_challenges(contest_id):
    
    #challenge_data = {}
    # import pdb; pdb.set_trace()
    data_raw = db.engine.execute(
        "select * from contests join contests_challenges on contests.id=contests_challenges.contest_id join challenges on contests_challenges.challenge_id=challenges.id where contests.id={}".format(contest_id))
    names = [dict(row) for row in data_raw]
    challenges_arr = []
    data = {}
    for i in names:
        challenge_data = {}
        data['contest_name'] = i['contest_name']
        data['contest_id'] = i['id']
        data['start_date'] = str(i['start'].strftime("%m/%d/%Y"))
        data['start_time'] = str(i['start'].strftime("%H:%M"))
        data['end_date'] = str(i['end'].strftime("%m/%d/%Y"))
        data['end_time'] = str(i['end'].strftime("%H:%M"))
        data['details'] = i['details']
        data['show_leaderboard'] = i['show_leaderboard']
        data['created_at'] = str(i['created_at'])
        challenge_data['description'] = i['description']
        challenge_data['challenge_id'] = i['challenge_id']
        challenge_data['problem_statement'] = i['problem_statement']
        challenge_data['input_format'] = i['input_format']
        challenge_data['output_format'] = i['output_format']
        challenge_data['difficulty'] = i['difficulty']
        challenge_data['sample_input'] = i['sample_input']
        challenge_data['sample_output'] = i['sample_output']
        challenge_data['created_at'] = str(
            i['created_at'].strftime("%m/%d/%Y"))
        challenges_arr.append(challenge_data)
        #data['challenges'] = challenges_arr
       # data_date =(names[0]['start'].strftime("%m/%d/%Y"))
    resp = {"data": challenges_arr, "contest_data": data}
    # for item in resp["data"]:
    #     print(item)
    return resp

def get_contests():
    print('in the contest')
    resp_data = []
    result_data = db.engine.execute("select *from contests")
    final_val = [dict(row) for row in result_data]
    print(final_val)
    for j in final_val:
        data = {}
        data["id"] = j['id']
        data["contest_name"] = j['contest_name']
        data['start_date'] = str(j['start'].strftime("%m/%d/%Y"))
        data['start_time'] = str(j['start'].strftime("%H:%M"))
        data['end_date'] = str(j['end'].strftime("%m/%d/%Y"))
        data['end_time'] = str(j['end'].strftime("%H:%M"))
        data['details'] = j['details']
        data['show_leaderboard'] = j['show_leaderboard']
        data['created_at'] = str(j['created_at'].strftime("%m/%d/%Y %H:%M"))
        resp_data.append(data)
    resp = {"contests": resp_data}
    return resp


def add_contest(data, contest_name, user_id):
    end = data['end_date']+" "+data['end_time']
    start = data['start_date']+" "+data['start_time']
    new_asset = ContestsModel(contest_name=contest_name, 
                                start=start,
                                end=end, 
                                details=data["details"], 
                                show_leaderboard=data["show_leaderboard"],
                                owner = user_id)

    save_changes(new_asset)
    print('add contest saved')
    contest_id = new_asset.id
    if contest_id == None:
        return False

    print('challenges added')
    for challenge_id in data["challenge_ids"]:
        new_asset = db.engine.execute(
            "insert into contests_challenges (challenge_id,contest_id) values ({},{})".format(challenge_id, contest_id))
    return True

def update_contest(data, contest_name, user_id):
    contest = ContestsModel.query.filter_by(contest_name = contest_name).first()

    if contest.owner == user_id:
        #update
        end = data['end_date']+" "+data['end_time']
        start = data['start_date']+" "+data['start_time']

        db.session.query(ContestsModel).filter(ContestsModel.id == contest.id).update({ContestsModel.start : start, ContestsModel.end : end, ContestsModel.details : data['details'], ContestsModel.show_leaderboard : data['show_leaderboard']})
        db.session.commit()

        challenges_db = []
        
        data_raw = db.engine.execute("select challenge_id from contests_challenges where contest_id = %s"%(contest.id))

        for row in data_raw:
            challenges_db.append(row['challenge_id'])

        for challenge_id in data["challenge_ids"]:
            if challenge_id in challenges_db:
                continue
            else:
                db.engine.execute("insert into contests_challenges (challenge_id,contest_id) values (%s,%s)"%(contest.id, challenge_id))
        
        deleted_challenges = []

        for cid in challenges_db:
            if cid in data['challenge_id']:
                continue
            else:
                db.execute.engine("Delete from contests_challenges where challenge_id = %s, contest_id = %s"%(cid, contest.id))
        return True
    else:
        print("User is not authorized for updating the contest!")
        return False