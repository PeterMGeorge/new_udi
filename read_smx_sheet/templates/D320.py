from read_smx_sheet.parameters import parameters as pm
from read_smx_sheet.app_Lib import functions as funcs
import traceback


def d320(cf, source_output_path, STG_tables, BKEY):
    file_name = funcs.get_file_name(__file__)
    f = funcs.WriteFile(source_output_path, file_name, "sql")
    try:
        separator = pm.stg_cols_separator
        stg_tables_df = STG_tables.loc[(STG_tables['Key domain name'] != "")
                                        & (STG_tables['Natural key'] != "")]

        for stg_tables_df_index, stg_tables_df_row in stg_tables_df.iterrows():
            key_domain_name = stg_tables_df_row['Key domain name']
            stg_table_name = stg_tables_df_row['Table name']
            stg_Column_name = stg_tables_df_row['Column name']

            Bkey_filter = str(stg_tables_df_row['Bkey filter']).upper()
            Bkey_filter = "WHERE " + Bkey_filter if Bkey_filter != "" and "JOIN" not in Bkey_filter else Bkey_filter
            Bkey_filter = Bkey_filter + "\n" if Bkey_filter != "" else Bkey_filter

            Natural_key_list = stg_tables_df_row['Natural key'].split(separator)
            trim_Trailing_Natural_key_list = []

            for i in Natural_key_list:
                trim_Trailing_Natural_key_list.append("TRIM(Trailing '.' from TRIM(" + i.strip() + "))")

            Source_Key = funcs.list_to_string(trim_Trailing_Natural_key_list, separator)
            coalesce_count = Source_Key.upper().count("COALESCE")
            separator_count = Source_Key.count(separator)

            compare_string = funcs.single_quotes("_" * separator_count) if coalesce_count > separator_count else "''"

            Source_Key_cond = "WHERE " if "WHERE" not in Bkey_filter else " AND "
            Source_Key_cond = Source_Key_cond + "COALESCE(Source_Key,"+compare_string+") <> "+compare_string+" "

            bkey_df = BKEY.loc[(BKEY['Key domain name'] == key_domain_name)]
            Key_set_ID = str(int(bkey_df['Key set ID'].values[0]))
            Key_domain_ID = str(int(bkey_df['Key domain ID'].values[0]))

            script = "REPLACE VIEW " + cf.INPUT_VIEW_DB + ".BK_" + Key_set_ID + "_" + stg_table_name + "_" + stg_Column_name + "_" + Key_domain_ID + "_IN AS LOCK ROW FOR ACCESS\n"
            script = script + "SELECT " + Source_Key + " AS Source_Key\n"
            script = script + "FROM " + cf.v_stg + "." + stg_table_name + "\n"
            script = script + Bkey_filter + Source_Key_cond + "\n"
            script = script + "GROUP BY 1;" + "\n"

            f.write(script)
            f.write('\n')

    except:
        funcs.TemplateLogError(cf.output_path, source_output_path, file_name, traceback.format_exc()).log_error()
    f.close()
