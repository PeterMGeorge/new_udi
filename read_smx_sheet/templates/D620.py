from read_smx_sheet.app_Lib import functions as funcs
from read_smx_sheet.app_Lib import TransformDDL
import traceback


def d620(cf, source_output_path, Table_mapping,Column_mapping,Core_tables, Loading_Type):
    file_name = funcs.get_file_name(__file__)
    f = funcs.WriteFile(source_output_path, file_name, "sql")
    try:
        notes= list()
        for table_maping_index, table_maping_row in Table_mapping.iterrows():

            inp_view_from_clause = ''

            process_type = 'TXF'
            layer = str(table_maping_row['Layer'])
            table_maping_name=str(table_maping_row['Mapping name'])
            src_layer=str(table_maping_row['Source layer'])
            process_name = process_type + "_" + layer + "_" + table_maping_name

            inp_view_header = 'REPLACE VIEW ' + cf.INPUT_VIEW_DB + '.' + process_name + '_IN AS LOCK ROW FOR ACCESS'
            target_table = str(table_maping_row['Target table name'])
            apply_type = table_maping_row['Historization algorithm']

            main_src = table_maping_row['Main source']
            main_src_alias = table_maping_row['Main source alias']

            if main_src == main_src_alias:
                main_src = cf.SI_VIEW + '.' + main_src
            # core_tables_list= pd.unique(list(Core_tables['Table name']))
            core_tables_list= TransformDDL.get_core_tables_list(Core_tables)

            if main_src is None:
                msg = 'Missing Main Source  for Table Mapping:{}'.format(str(table_maping_row['Mapping name']))
                notes += msg
                continue

            if target_table not in core_tables_list:
                msg='TARGET TABLE NAME not found in Core Tables Sheet for Table Mapping:{}'.format(str(table_maping_row['Mapping name']))
                notes += msg
                continue

            sub = "/* Target table:\t" + target_table + "*/" + '\n'\
                  + "/* Table mapping:\t" + table_maping_name + "*/" + '\n'\
                  + "/* Mapping group:\t" + table_maping_row['Mapping group'] + "*/" + '\n' \
                  + "/* Apply type:\t\t" + apply_type + "*/"
            inp_view_select_clause='SELECT ' +'\n' + sub + TransformDDL.get_select_clause(target_table, Core_tables, table_maping_name, Column_mapping)
            map_grp = ' CAST(' +funcs.single_quotes(table_maping_row['Mapping group'])+' AS VARCHAR(100)) AS  MAP_GROUP ,'
            start_date = '(SELECT Business_Date FROM ' + cf.GCFR_V + '.GCFR_Process_Id'+'\n'+'   WHERE Process_Name = ' + "'" + process_name + "'"+'\n'+') AS Start_Date,'
            end_date='DATE '+"'9999-12-31'"+' AS End_Date,'

            if Loading_Type == 'OFFLINE':
                modification_type = "'U' AS MODIFICATION_TYPE"
            else:
                modification_type = main_src_alias + '.MODIFICATION_TYPE'

            inp_view_select_clause=inp_view_select_clause+'\n'+ map_grp+'\n'+start_date+ '\n'+end_date+ '\n'+modification_type+'\n'

            if table_maping_row['Join'] == "":
                inp_view_from_clause = 'FROM ' + main_src + ' ' + main_src_alias
            elif table_maping_row['Join'] != "":
                if (table_maping_row['Join'].find("FROM".strip()) == -1): #no subquery in join clause
                    inp_view_from_clause = 'FROM ' + main_src + ' ' + main_src_alias
                    inp_view_from_clause = inp_view_from_clause+'\n'+table_maping_row['Join']
                    join = 'JOIN '+cf.SI_VIEW+'.'
                    inp_view_from_clause = inp_view_from_clause.replace('JOIN ',join)
                else:
                    sub_query_flag=1
                    join_clause=table_maping_row['Join']
                    subquery_clause= TransformDDL.get_sub_query(cf, join_clause, src_layer, main_src)
                    inp_view_from_clause = ' FROM \n'+ subquery_clause

            inp_view_where_clause=';'
            if table_maping_row['Filter criterion']!="":
                # if (sub_query_flag == 0):
                inp_view_where_clause = 'Where '+table_maping_row['Filter criterion']+';'
                # else:
                #     inp_view_where_clause = 'Where '+table_maping_row['Filter criterion']+');'


            f.write(inp_view_header)
            f.write("\n")
            f.write(inp_view_select_clause)
            f.write("\n")
            f.write( inp_view_from_clause)
            f.write("\n")
            f.write(inp_view_where_clause)
            f.write("\n")
            f.write("\n")
            f.write("\n")

    except:
        funcs.TemplateLogError(cf.output_path, source_output_path, file_name, traceback.format_exc()).log_error()

    f.close()









