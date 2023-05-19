#!/usr/bin/env python3
"""
script to go through all the data, and add a comment to the records from the old book.

The comment says:

"The data in this record may have been compiled from multiple sources and may
thus may reflect samples of varying age and composition.
"
"""
import adios_db.scripting as ads

# OLD_COMMENT = ("The data in this record may have been compiled from "
#                "multiple sources and may thus may reflect samples of "
#                "varying age and composition."
#                )

NEW_COMMENT = ("The data in this record may have been compiled "
               "from multiple sources and reflect samples of "
               "varying age and composition.")

USAGE = """
add_note_on_old_ests_record [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = ads.process_input(USAGE)
    count = 0

    for rec, pth in ads.get_all_records(base_dir):
        # print("\n\n******************\n")
        # print("processing:", rec.oil_id)
        # print("API is:", rec.metadata.API)
        reference = rec.metadata.reference

        if (reference.year in {1990, 1996, 1990, 1999, 1992}
                and "Jokuty" in reference.reference):
            # rec.metadata.comments = "\n".join((rec.metadata.comments,
            #                                    ADDED_COMMENT)).strip()

            if NEW_COMMENT not in rec.metadata.comments:
                count += 1

                if rec.metadata.comments:
                    rec.metadata.comments = "\n\n".join((
                        rec.metadata.comments,
                        NEW_COMMENT
                    ))
                else:
                    rec.metadata.comments = NEW_COMMENT

                print("Adding note to:", rec.oil_id)
                print(reference.reference)

            # rec.metadata.comments = rec.metadata.comments.replace(OLD_COMMENT,
            #                                                       NEW_COMMENT)
            if not dry_run:
                print("Saving out:", pth)
                rec.to_file(pth)
            else:
                print("Nothing saved")

    print(f"{count} records changed")


if __name__ == "__main__":
    main()
