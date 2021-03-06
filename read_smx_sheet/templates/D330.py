from read_smx_sheet.app_Lib import functions as funcs
import traceback


def d330(cf, source_output_path, STG_tables, BKEY):
    file_name = funcs.get_file_name(__file__)
    f = funcs.WriteFile(source_output_path, file_name, "sql")
    try:
        stg_tables_df = STG_tables.loc[(STG_tables['Key domain name'] != "")
                                       & (STG_tables['Natural key'] != "")]

        for stg_tables_df_index, stg_tables_df_row in stg_tables_df.iterrows():
            key_domain_name = stg_tables_df_row['Key domain name']
            stg_table_name = stg_tables_df_row['Table name']
            stg_Column_name = stg_tables_df_row['Column name']

            bkey_df = BKEY.loc[(BKEY['Key domain name'] == key_domain_name)]
            key_set_name = bkey_df['Key set name'].values[0]
            Key_set_ID = str(int(bkey_df['Key set ID'].values[0]))
            Key_domain_ID = str(int(bkey_df['Key domain ID'].values[0]))
            Physical_table = bkey_df['Physical table'].values[0]

            script = "EXEC " + cf.MACRO_DB + ".GCFR_Register_Process("
            script = script + "'BK_" + Key_set_ID + "_" + stg_table_name + "_" + stg_Column_name + "_" + Key_domain_ID + "',"
            script = script + "'define bkey for the table " + key_set_name + " and the domain " + key_domain_name + "',"
            script = script + str(cf.gcfr_bkey_process_type) + ","
            script = script + str(cf.gcfr_ctl_Id) + ","
            script = script + str(cf.gcfr_stream_key) + ","
            script = script + "'" + cf.INPUT_VIEW_DB + "',"
            script = script + "'BK_" + Key_set_ID + "_" + stg_table_name + "_" + stg_Column_name + "_" + Key_domain_ID + "_IN',"
            script = script + "'" + cf.UTLFW_v + "',"
            script = script + "'" + Physical_table + "',"
            script = script + "'" + cf.UTLFW_t + "',"
            script = script + "'" + Physical_table + "',"
            script = script + "'" + cf.TMP_DB + "',"
            script = script + "'" + Key_set_ID + "',"
            script = script + "'" + Key_domain_ID + "',"
            script = script + "'',0,0,0,0);"

            f.write(script + '\n')
    except:
        funcs.TemplateLogError(cf.output_path, source_output_path, file_name, traceback.format_exc()).log_error()
    f.close()
