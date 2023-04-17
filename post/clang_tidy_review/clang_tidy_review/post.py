#!/usr/bin/env python3

# clang-tidy review - post comments
# Copyright (c) 2022 Peter Hill
# SPDX-License-Identifier: MIT
# See LICENSE for more information

import argparse
import pprint

from clang_tidy_review import (
    PullRequest,
    load_review,
    post_review,
    load_metadata,
    strip_enclosing_quotes,
    download_artifacts,
    post_annotations,
    bool_argument,
)


def main():
    parser = argparse.ArgumentParser(
        description="Post a review based on feedback generated by the clang-tidy-review action"
    )

    parser.add_argument("--repo", help="Repo name in form 'owner/repo'")
    parser.add_argument(
        "--max-comments",
        help="Maximum number of comments to post at once",
        type=int,
        default=25,
    )
    parser.add_argument(
        "--lgtm-comment-body",
        help="Message to post on PR if no issues are found. An empty string will post no LGTM comment.",
        type=str,
        default='clang-tidy review says "All clean, LGTM! :+1:"',
    )
    parser.add_argument("--token", help="github auth token")
    parser.add_argument(
        "--dry-run", help="Run and generate review, but don't post", action="store_true"
    )
    parser.add_argument(
        "--workflow_id",
        help="ID of the workflow that generated the review",
        default=None,
    )
    parser.add_argument(
        "--annotations",
        help="Use annotations instead of comments",
        type=bool_argument,
        default=False,
    )

    args = parser.parse_args()

    pull_request = PullRequest(args.repo, None, args.token)

    # Try to read the review artifacts if they're already present
    metadata = load_metadata()
    review = load_review()

    # If not, try to download them automatically
    if metadata is None and args.workflow_id is not None:
        print("Attempting to automatically download review artifacts", flush=True)
        metadata, review = download_artifacts(pull_request, int(args.workflow_id))

    if metadata is None:
        raise RuntimeError("Couldn't find review metadata")

    pull_request.pr_number = metadata["pr_number"]

    print(
        "clang-tidy-review generated the following review",
        pprint.pformat(review, width=130),
        flush=True,
    )

    if args.annotations:
        post_annotations(pull_request, review)
    else:
        lgtm_comment_body = strip_enclosing_quotes(args.lgtm_comment_body)
        post_review(
            pull_request, review, args.max_comments, lgtm_comment_body, args.dry_run
        )


if __name__ == "__main__":
    main()
