import json
import argparse
import subprocess
import logging
import shutil


def parse_catalog(catalog):
    distributions = []
    for dataset in catalog['dataset']:
        for distribution in dataset['distribution']:
            if distribution['format'] == 'subscription':
                if 'deploymentProperties' in distribution:
                    if 'pushConfig' in distribution['deploymentProperties']:
                        distributions.append(distribution)
    return distributions


def update_subscription(args):
    try:
        with open(args.data_catalog, 'r') as f:
            catalog = json.load(f)

        distributions = parse_catalog(catalog)

        # Iterate distributions and add to modify-push-config cmd
        for dist in distributions:
            cmd = ['gcloud', 'beta', 'pubsub', 'subscriptions', 'update']
            cmd.append(dist['title'])
            cmd.append('--project={}'.format(args.project_id))

            # Add pushEndpoint to cmd
            if 'pushEndpoint' in dist['deploymentProperties']['pushConfig']:
                cmd.append('--push-endpoint={}'.format(
                    dist['deploymentProperties']['pushConfig']['pushEndpoint']))

            if 'oidcToken' in dist['deploymentProperties']['pushConfig']:
                # Add serviceAccountEmail to cmd
                if 'serviceAccountEmail' in dist['deploymentProperties']['pushConfig']['oidcToken']:
                    cmd.append('--push-auth-service-account={}'.format(
                        dist['deploymentProperties']['pushConfig']['oidcToken']['serviceAccountEmail']))
                # Add audience to cmd
                if 'serviceAccountEmail' in dist['deploymentProperties']['pushConfig']['oidcToken']:
                    cmd.append('--push-auth-token-audience={}'.format(
                        dist['deploymentProperties']['pushConfig']['oidcToken']['audience']))

            if 'ackDeadlineSeconds' in dist['deploymentProperties']:
                cmd.append('--ack-deadline={}'.format(
                    dist['deploymentProperties']['ackDeadlineSeconds']))

            print('Executing command: ' + ' '.join(cmd))
            subprocess.call(cmd)

        if not distributions:
            print('No subscription found to update')

    except Exception as e:
        print('Unable to update subscription: {}'.format(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-catalog', required=True)
    parser.add_argument('-p', '--project-id', required=True)
    args = parser.parse_args()
    update_subscription(args)
