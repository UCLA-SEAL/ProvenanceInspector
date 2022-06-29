
import pandas as pd

class InferQuery:
    def __init__(self):
        self.out_df = pd.read_csv('../results/log.csv')[
            ['original_text', 'perturbed_text', 'result_type']]

        transformation_log = pd.read_csv('../results/transformation.csv', 
            index_col=0, names = ["transformation_id","transformation_type",
            "prev_text", "after_text", "prev_target", "after_target",
            "from_modified_indices", "to_modified_indices", "changes"])

        self.edge_to_transformation = transformation_log.set_index(['prev_text', 'after_text'])

        edges_df = transformation_log[['prev_text','after_text']]
        self.forward_edges_df = edges_df.set_index('prev_text')
        self.backward_edges_df = edges_df.set_index('after_text')

        self.id_to_text = pd.read_csv('../results/text.csv', index_col="text_id", 
            names = ["text_id", "text"])
        self.text_to_id = pd.read_csv('../results/text.csv', index_col="text", 
            names = ["text_id", "text"])

    def get_trace_of_output(self, result_text: str):
        cur_text_id = self.text_to_id.loc[result_text]['text_id']
        trace = []
        while cur_text_id in self.backward_edges_df.index:
            trace.append((cur_text_id, self.id_to_text.loc[cur_text_id]['text']))
            cur_text_id = self.backward_edges_df.loc[cur_text_id]['prev_text']
        trace.append((cur_text_id, self.id_to_text.loc[cur_text_id]['text']))

        trace = trace[::-1]
        trace_w_transformatiosn = []
        for i in range(len(trace) - 1):
            row=self.edge_to_transformation.loc[trace[i][0], trace[i+1][0]]
            #from_to = row[["from_modified_indices", "to_modified_indices"]].values
            trans_name = row["transformation_type"]

            #trace_w_transformatiosn += [trace[i], f"{trans_name}: {from_to[0]}-->{from_to[1]}"]
            trace_w_transformatiosn += [trace[i], f"{trans_name}"]

        trace_w_transformatiosn.append(trace[-1])
        return trace_w_transformatiosn


    def get_trace_of_output_idx(self, result_idx: int):
        query_output = self.out_df.loc[result_idx]['perturbed_text']
        return self.get_trace_of_output(query_output)


    def get_traces_of_all_outputs(self):
        all_traces = []
        for i in range(self.out_df.shape[0]):
            row = self.out_df.iloc[i]
            if row['result_type'] != 'Skipped':
                all_traces.append(self.get_trace_of_output(row['perturbed_text']))
        return all_traces
