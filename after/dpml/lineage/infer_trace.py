
import pandas as pd
import os.path as osp

class InferQuery:
    def __init__(self, dir_pth = '../results/'):
        self.out_df = pd.read_csv(osp.join(dir_pth, 'log.csv'))[
            ['original_text', 'perturbed_text', 'original_output','perturbed_output',
            'result_type']]

        transformation_log = pd.read_csv(osp.join(dir_pth, 'transformation.csv'), 
            index_col=0, names = ["transformation_id","transformation",
            "prev_text", "after_text", "prev_target", "after_target",
            "from_modified_indices", "to_modified_indices", "changes"])

        self.edge_to_transformation = transformation_log.set_index(['prev_text', 'after_text'])

        edges_df = transformation_log[['prev_text','after_text']]
        self.forward_edges_df = edges_df.set_index('prev_text')
        self.backward_edges_df = edges_df.set_index('after_text')

        self.id_to_text = pd.read_csv(osp.join(dir_pth, 'text.csv'), index_col="text_id", 
            names = ["text_id", "text"])
        self.text_to_id = pd.read_csv(osp.join(dir_pth, 'text.csv'), index_col="text", 
            names = ["text_id", "text"])


    def get_transfromation_history(self, result_record):

        text_trace = [result_record.text]
        cur_record = result_record
        while cur_record.prev:
            cur_record = cur_record.prev
            text_trace.append(cur_record)
        text_trace = text_trace[::-1]
        
        history = result_record.transformation_provenance.history
        transformation_info = [{}] * len(history)
        for trans in history:
            transformation_info[trans[0]] = (trans[1])

        feature_history = result_record.feature_provenance.history

        trace = [()] * len(feature_history)
        edit_trace = [()] * len(feature_history)

        for i,record in enumerate(feature_history):
            tag = record[2]
            parts = tag.split(': ')
            op = parts[0]
            tag = parts[1]
            if op == 'replace' or op == 'insert':
                spans = tag[1:-1].split(']-[')
                from_span = tuple(map(int, spans[0].split(',')))
                to_span = tuple(map(int, spans[1].split(',')))
                
            elif op == 'delete':
                from_span = tuple(map(int, tag[1:-1].split(',')))
                to_span= tuple()

            from_inds = list(range(*from_span))

            if len(to_span) > 0:
                to_inds = list(range(*to_span))
            else:
                to_inds = []

            trace[record[0]] = (transformation_info[i], from_inds, to_inds)
            edit_trace[record[0]] = (op, from_span, to_span)
        
        all_trace = []
        for i in range(len(trace)):
            all_trace += [text_trace[i], trace[i], edit_trace[i]]
        all_trace += [text_trace[-1]]

        return all_trace


    def get_trace_of_output(self, result_text: str, from_label, to_label):
        cur_text_id = self.text_to_id.loc[result_text]['text_id']
        cur_label = to_label
        trace = []
        while cur_text_id in self.backward_edges_df.index:
            trace.append((cur_text_id, self.id_to_text.loc[cur_text_id]['text'], cur_label))
            cur_label = from_label
            cur_text_id = self.backward_edges_df.loc[cur_text_id]['prev_text']
        trace.append((cur_text_id, self.id_to_text.loc[cur_text_id]['text'], from_label))

        trace = trace[::-1]
        trace_w_transformation = []
        for i in range(len(trace) - 1):
            row=self.edge_to_transformation.loc[trace[i][0], trace[i+1][0]]
            edits = row["changes"][1:-1].split(', ')
            actual_edits = []
            for edit in edits:
                parts = edit[1:-1].split(': ')
                op = parts[0]
                tag = parts[1]
                if op == 'replace' or op == 'insert':
                    spans = tag[1:-1].split(']-[')
                    from_span = tuple(map(int, spans[0].split(',')))
                    to_span = tuple(map(int, spans[1].split(',')))
                    
                elif op == 'delete':
                    from_span = tuple(map(int, tag[1:-1].split(',')))
                    to_span= tuple()
                actual_edits.append((op, from_span, to_span))
            

            from_to = row[["from_modified_indices", "to_modified_indices"]].values
            trans_type = row["transformation"]

            trace_w_transformation += [trace[i], (trans_type, from_to[0], from_to[1]), actual_edits]

        trace_w_transformation.append(trace[-1])
        return trace_w_transformation


    def get_trace_of_output_idx(self, result_idx: int):
        output_text = self.out_df.loc[result_idx]['perturbed_text']
        from_label = self.out_df.loc[result_idx]['original_output']
        to_label = self.out_df.loc[result_idx]['perturbed_output']
        return self.get_trace_of_output(output_text, from_label, to_label)


    def get_traces_of_all_outputs(self):
        all_traces = []
        for i in range(self.out_df.shape[0]):
            row = self.out_df.iloc[i]
            if row['result_type'] != 'Skipped':
                all_traces.append(self.get_trace_of_output_idx(i))
        return all_traces
