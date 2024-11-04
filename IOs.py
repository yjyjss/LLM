from datetime import datetime
import pandas as pd
import csv
import json
import pdb
import numpy as np
import random

def var4prompt(df_list, n=5):
    """ Assign value to variables in the prompt
        Input: list contains 5 df, each df has consecutive 11 events
               n is the length of df_list, the first 4 frames are samples, the 5th is sample to predict
        Output: Dict variables, the keys are:
                                example_1
                                event_1
                                label_1
                                ...
                                example_4
                                event_4
                                label_4
                                
                                task_precedings
                                task_event
                                  """
    context = {}
    for i in range(n-1):
        
        df = df_list[i]
        array_df = df.to_numpy() # convert df to a array
        
        context[f"example_{i+1}"] = array_df[0:10,0:5]
        context[f"event_{i+1}"]   = array_df[10][0:5]
        context[f"label_{i+1}"]   = array_df[10][5]
        
    prediction_seq = df_list[n-1].to_numpy()
    context[f"task_precedings"] = prediction_seq[0:10,0:5]
    context[f"task_event"]      = prediction_seq[10,0:5]
    
    return context          
    
    
    
    
    # variables = {}
    
    # for i in range(5):
    #     df = df_list[i]
    #     array_df = df.to_numpy() # convert df to a array
        
    #     variables[f"example_preceding_events_{i+1}"] = array_df[0:10,0:5]
    #     variables[f"example_current_event_{i+1}"]    = array_df[10][0:5]
    #     variables[f"example_current_label_{i+1}"]    = array_df[10][5]
        
    # return variables

def summizeCorpus(df):
    # summarize for the events at the same ip address
    # return: list results
    # Initialize variables
    start_time = df.iloc[0]['time']
    pre_event  = df.iloc[0]['name']
    pre_host   = df.iloc[0]['host']
    pre_short  = df.iloc[0]['short']
    pre_label  = df.iloc[0]['time_label']
    count = 1
    
    results = []
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        if (row['name'] == pre_event) and (row['host'] == pre_host) and (row['short'] == pre_short) and (row['time_label'] == pre_label):
            count += 1
        else:
            end_time = df.iloc[i-1]['time']
            results.append(f"{start_time}-{end_time}  {pre_event}  {pre_host} {pre_short}  {pre_label}  counts:{count}")
            
            # reset start time
            start_time = row['time']
            pre_event  = row['name']
            pre_host   = row['host']
            #pre_short  = row['short']
            pre_label  = row['time_label']
            count = 1
    end_time = df.iloc[-1]['time']
    results.append(f"{start_time}-{end_time}  {pre_event}  {pre_host}  {pre_label}  counts:{count}")
    
    return results
            
            

def create_eventsType_level_description(json_file, txt_file):
    events_json = load_events_json_file(json_file)
    pass
    


def load_events_txt_file(txt_file):
    df = pd.read_csv(txt_file)
    df_unique = df.drop_duplicates()
    df_unique = df_unique.reset_index(drop=True)
    return df_unique

def groupby_ip_event(df,abbr1 = 'ip', abbr2='short'):
    
    grouped_df = df.groupby([abbr1,abbr2])
    
    return grouped_df

def create_one_sequence(df, n=11):
    """ input: dataframe
        return: dataframe or None """
    df_len = df.shape[0]
    
    if df_len > n:
        start_index = random.randint(0, df_len -n)
        selected_sequence = df.iloc[start_index:start_index + n]
        return selected_sequence

    
def create_sequences(df_grouped, seq_len=11, example_num=5):
    """ input: grouped dataframe by ip and event name
        output: example_list[[sample1_seq1,sample1_seq2,sample1_seq3,sample1_seq4,sample1_seq5],[sample2_seq1,sample2_seq2,sample2_seq3,sample2_seq4,sample2_seq5]],
                seq1 is a dataframe"""
                
    examples_list =[]
    for name, group in df_grouped:
        temp_list = []
        if group.shape[0]>seq_len:
            for i in range(example_num):
                example = create_one_sequence(group) 
                temp_list.append(example)
                
            examples_list.append(temp_list)
            
    return examples_list
        
        
        
        
        
        
        
    
    
    

def generate_sequences(seq, context_len=10):
    result = []
    for i in range(len(seq)):
        start = max(0,i-(context_len-1))
        sequence = seq[start:i+1]
        while len(sequence) < context_len:
            sequence.insert(0,sequence[0])
        result.append(sequence)
    result_array = np.array(result)
    return result_array
    

def load_intervals_and_labels(filename):
    """ filename: the interval file
        return: lists of intervals with 'sce, attack type, start time, and end_time"""
    intervals = []
    with open(filename,'r') as file:
        reader = csv.reader(file)
        next(reader)  # the first line is the title line
        for row in reader:  
            sce = row[0]
            attack_type = row[1]
            start_time = int(float(row[2]))
            end_time = int(float(row[3]))
            intervals.append((sce,attack_type,start_time, end_time))
    return intervals

def load_events_json_file(json_file):
    events_list = []

    with open(json_file,'r') as ts_file:
        for line in ts_file:
            events_list.append(json.loads(line))
    
    return events_list
    
def find_label_for_timestamp(scene, timestamp, intervals):
    """ scene, timestamp: belong to the 'timestamps' file, that is the events file; intervals belongs to the 'intervals' file, that contains the labels 
    return the label of one scene  """
    for scene_name, attack_type, start_time,end_time in intervals:
        if scene_name == scene and start_time <= timestamp <= end_time:
            return attack_type 
    return "false_positive"
        
def label_timestamps(events_file, intervals_file, output_file, sce='wilson'):
    """ Create label files   """
    
    intervals = load_intervals_and_labels(intervals_file)
    data = load_events_json_file(events_file)
    scene = sce
    
    # with open(events_file,'r') as ts_file, open(output_file,'w') as out_file:
    #     data = []
    #     for line in ts_file:
    #         data.append(json.loads(line))
    with open(output_file,'w') as out_file:
        for item in data[0:10]:       # data[0:10] only for testing
            timestamp = unix_time_converter(item['@timestamp'])
            label = find_label_for_timestamp(scene, timestamp, intervals)
            out_file.write(f"{timestamp},{label}\n")              
    
def unix_time_converter(time_str):
    """ Convert time to unix time format"""
    
    dt = datetime.strptime(time_str,"%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = int(dt.timestamp())
    
    return timestamp
    
def events_log_with_label(events_file, labels_file, output_file,sequence_length=10):
    """Create log sequences. The length is set to be 10 defaultly
        Output: events sequences with following format:
        log1, log2,...,log10, label"""
        
    events = load_events_json_file(events_file)
    #logs =[log for log ]
        
def extract_example_logs(log_sequences_file,output_file):
    pass
    
    
    